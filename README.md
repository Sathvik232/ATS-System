Rule Engine Application with Abstract Syntax Tree (AST) - README

This application is a Flask-based rule engine that evaluates user eligibility based on complex, customizable rules. It uses an Abstract Syntax Tree (AST) for structured rule representation and supports dynamic rule creation, combination, and evaluation.

---

 Application Architecture

Layers:

1. UI Layer:
   - Manages rule visualization and user interactions for creating, modifying, and viewing rules.

2. API Layer:
   - Provides endpoints for creating, combining, and evaluating rules dynamically.

3. Database Layer:
   - Stores rules in a structured format, including both the rule strings and AST representations in JSON.

Endpoints and Functions:

- `/get_rules`: Fetches all rules from the database.
- `/create_rule`: Parses the rule string into an AST and stores it in the database.
- `/combine_rules`: Combines multiple rules into a single AST, supporting complex eligibility criteria.
- `/evaluate_rule`: Evaluates the eligibility of a user based on input data against a specified AST.

---

AST Representation:

- Each rule’s AST is represented using `Node` objects. These nodes include:
  - Operators: Logical operations like `AND` and `OR`.
  - Operands: Conditions such as `age > 30` or `department = 'Sales'`.
- AST operations handle complex nested conditions and prevent redundancy in rule evaluation.

Example:

A rule such as `(age > 30 AND department = 'Sales')` would be represented as:

```json
{
  "type": "operator",
  "value": "AND",
  "left": {
    "type": "operand",
    "value": "age > 30"
  },
  "right": {
    "type": "operand",
    "value": "department = 'Sales'"
  }
}
```

---

Error Handling and Validation:

- The system includes checks for malformed rules, invalid attribute values, and database operation failures.
- Response codes:
  - 400: Bad requests, e.g., malformed rules.
  - 500: Server errors.

---

 Improvements and Considerations:

1. Testing:
   - Unit tests should be added for each function, particularly for parsing and evaluating rules.

2. Data Validation:
   - Improved validation in `evaluate_rule` to ensure that data types (e.g., integer for `age`) match rule conditions.

3. Performance:
   - To improve performance under high load, consider caching frequently used rules or optimizing the rule engine.

---

 Future Extensions:

1. User-Defined Functions (UDFs):
   - Allowing user-defined functions within rules could offer greater flexibility, enabling custom evaluation logic.

2. Rule Versioning:
   - Adding versioning for rules would allow rollback capabilities and better tracking of rule changes.

---

 Example API Usage

# 1. Create Rule

Endpoint: `/create_rule`

Request:
```json
{
  "rule_string": "(age > 30 AND department = 'Sales')"
}
```

Response:
```json
{
  "ast": {
    "type": "operator",
    "value": "AND",
    "left": {
      "type": "operand",
      "value": "age > 30"
    },
    "right": {
      "type": "operand",
      "value": "department = 'Sales'"
    }
  }
}
```

# 2. Combine Rules

Endpoint: `/combine_rules`

Request:
```json
{
  "rules": [
    "((age > 30 AND department = 'Sales') OR (age < 25 AND department = 'Marketing')) AND (salary > 50000 OR experience > 5)",
    "((age > 30 AND department = 'Marketing')) AND (salary > 20000 OR experience > 5)"
  ]
}
```

Response:
```json
{
  "combined_ast": {
    "type": "operator",
    "value": "AND",
    "left": {
      // Nested JSON structure for the combined AST
    }
  }
}
```

# 3. Evaluate Rule

Endpoint: `/evaluate_rule`

Request:
```json
{
  "ast": {
    "type": "operator",
    "value": "OR",
    "left": {
      "type": "operator",
      "value": "AND",
      "left": {
        "type": "operand",
        "value": "age > 30"
      },
      "right": {
        "type": "operand",
        "value": "department = 'Sales'"
      }
    },
    "right": {
      "type": "operand",
      "value": "income < 50000"
    }
  },
  "data": {
    "age": 35,
    "department": "Sales",
    "income": 45000
  }
}
```

Response:
```json
{
  "is_eligible": true
}
```

# 4. Get Rules

Endpoint: `/get_rules`

Response:
```json
{
  "rules": [
    {
      "id": 1,
      "rule_string": "(age > 30 AND department = 'Sales')",
      "ast_json": "{...AST representation in JSON...}"
    },
    {
      "id": 2,
      "rule_string": "(age > 30 AND department = 'Sales')",
      "ast_json": "{...AST representation in JSON...}"
    }
  ]
}
```

---

 Setup

1. Clone the Repository:
   ```bash
   git clone <repository-url>
   cd rule-engine-ast
   ```

2. Install Dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the Application:
   ```bash
   python app.py
   ```

---

 Contributing

Feel free to submit issues, feature requests, and pull requests. Before contributing, please ensure that your changes are well-tested.

---

 License

This project is licensed under the MIT License.

---

This README provides a structured overview of the application and its functionality for contributors and users. Let me know if you want any further customization!
