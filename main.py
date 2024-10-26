from flask import Flask, request, jsonify
import json
import mysql.connector

app = Flask(__name__)

class Node:

    """Represents a node in the AST"""

    def __init__(self, node_type, left=None, right=None, value=None):
        self.type = node_type  # "operator" or "operand"
        self.left = left
        self.right = right
        self.value = value  # For operands (e.g., "age > 30"), this stores the condition

    def to_dict(self):
        """Convert Node to a dictionary for JSON representation."""
        return {
            "type": self.type,
            "value": self.value,
            "left": self.left.to_dict() if self.left else None,
            "right": self.right.to_dict() if self.right else None,
        }

    def __repr__(self):
        return json.dumps(self.to_dict(), indent=2)  # Pretty JSON format for debugging


class RuleEngine:
    """Rule engine to parse rules, combine them, and evaluate conditions"""

    def create_rule(self, rule_string):
        """
        Parses a rule string and converts it into an AST.
        Example: "(age > 30 AND department = 'Sales')" into an AST.
        """
        tokens = rule_string.split()

        def parse_expression(tokens):
            # Parse tokens to create AST nodes
            if 'AND' in tokens:
                index = tokens.index('AND')
                left = parse_expression(tokens[:index])
                right = parse_expression(tokens[index + 1:])
                return Node("operator", left, right, "AND")
            elif 'OR' in tokens:
                index = tokens.index('OR')
                left = parse_expression(tokens[:index])
                right = parse_expression(tokens[index + 1:])
                return Node("operator", left, right, "OR")
            else:
                return Node("operand", value=" ".join(tokens))

        return parse_expression(tokens)

    def combine_rules(self, rules):
        """
        Combines multiple ASTs into a single AST using "AND" logic.
        """
        if not rules:
            return None
        combined_ast = self.create_rule(rules[0])
        for rule in rules[1:]:
            rule_ast = self.create_rule(rule)
            combined_ast = Node("operator", left=combined_ast, right=rule_ast, value="AND")
        return combined_ast

    def evaluate_rule(self, ast, data):
        """
        Recursively evaluates the AST against provided data.
        Returns True if the data satisfies the rule, otherwise False.
        """
        if ast.type == "operand":
            # Parse operand (e.g., "age > 30")
            attribute, operator, value = ast.value.split()
            value = int(value) if value.isdigit() else value.strip("'")
            attribute_value = data.get(attribute)
            if operator == '>':
                return attribute_value > value
            elif operator == '<':
                return attribute_value < value
            elif operator == '=':
                return attribute_value == value
            return False
        elif ast.type == "operator":
            if ast.value == "AND":
                return self.evaluate_rule(ast.left, data) and self.evaluate_rule(ast.right, data)
            elif ast.value == "OR":
                return self.evaluate_rule(ast.left, data) or self.evaluate_rule(ast.right, data)
        return False


# Initialize RuleEngine
engine = RuleEngine()
db_config = {
        'user': 'sathvik',
        'password': 'user_123',
        'host': 'localhost',
        'database': 'rule_engine'
    }

@app.route('/get_rules', methods=['GET'])
def get_rules():
    # Connect to MySQL
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)  # dictionary=True returns rows as dictionaries
    if conn.is_connected():
        print("Connected")

    try:
        # Execute query to fetch all rules
        cursor.execute("SELECT id, rule_string, ast_json FROM rules")
        rules = cursor.fetchall()  # Fetch all results
    except mysql.connector.Error as err:
        return jsonify({"error": str(err)}), 500
    finally:
        cursor.close()
        conn.close()

    # Return the list of rules as JSON
    return jsonify({"rules": rules})

# API to create rule
@app.route('/create_rule', methods=['POST'])
def create_rule():
    rule_string = request.json.get("rule_string")
    if not rule_string:
        return jsonify({"error": "rule_string is required"}), 400
    ast = engine.create_rule(rule_string)
    ast_json = json.dumps(ast.to_dict())
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()

    try:
        # Insert rule data into database
        cursor.execute("INSERT INTO rules (rule_string, ast_json) VALUES (%s, %s)", (rule_string, ast_json))
        conn.commit()
        #rule_id = cursor.lastrowid  # Get the ID of the inserted row
    except mysql.connector.Error as err:
        conn.rollback()
        return jsonify({"error": str(err)}), 500
    finally:
        cursor.close()
        conn.close()
    return jsonify({"ast": ast.to_dict()})

# API to combine rules
@app.route('/combine_rules', methods=['POST'])
def combine_rules():
    rules = request.json.get("rules")
    if not rules or not isinstance(rules, list):
        return jsonify({"error": "A list of rules is required"}), 400
    combined_ast = engine.combine_rules(rules)
    return jsonify({"combined_ast": combined_ast.to_dict()})

@app.route('/evaluate_rule', methods=['POST'])
def evaluate_rule():
    ast = request.json.get("ast")
    data = request.json.get("data")
    if not ast or not data:
        return jsonify({"error": "Both ast and data are required"}), 400

    # Rebuild AST from JSON
    def dict_to_node(d):
        if d is None:
            return None
        node = Node(d["type"], value=d["value"])
        node.left = dict_to_node(d.get("left"))
        node.right = dict_to_node(d.get("right"))
        return node

    ast_node = dict_to_node(ast)
    result = engine.evaluate_rule(ast_node, data)
    return jsonify({"is_eligible": result})



if __name__ == '__main__':
    app.run(debug=True)

