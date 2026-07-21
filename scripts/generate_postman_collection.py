import json
import os

collection = {
    "info": {
        "name": "Edu RAG API - Auth & Courses",
        "description": "Postman Collection for testing Happy & Error cases of Auth and Course modules.",
        "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
    },
    "variable": [
        {
            "key": "base_url",
            "value": "http://localhost:8000/api/v1",
            "type": "string"
        },
        {
            "key": "token",
            "value": "",
            "type": "string"
        }
    ],
    "item": [
        {
            "name": "1. Authentication",
            "item": [
                {
                    "name": "Register (Happy Case)",
                    "request": {
                        "method": "POST",
                        "header": [{"key": "Content-Type", "value": "application/json"}],
                        "body": {
                            "mode": "raw",
                            "raw": json.dumps({"email": "newuser@gmail.com", "password": "123", "full_name": "New User"})
                        },
                        "url": {"raw": "{{base_url}}/auth/register", "host": ["{{base_url}}"], "path": ["auth", "register"]}
                    },
                    "event": [{"listen": "test", "script": {"exec": ["pm.test('Status code is 200 or 400 (if exist)', function () { pm.expect(pm.response.code).to.be.oneOf([200, 400]); });"]}}]
                },
                {
                    "name": "Login - Admin (Happy Case)",
                    "request": {
                        "method": "POST",
                        "header": [{"key": "Content-Type", "value": "application/x-www-form-urlencoded"}],
                        "body": {
                            "mode": "urlencoded",
                            "urlencoded": [
                                {"key": "username", "value": "admin@gmail.com", "type": "text"},
                                {"key": "password", "value": "admin123", "type": "text"}
                            ]
                        },
                        "url": {"raw": "{{base_url}}/auth/login", "host": ["{{base_url}}"], "path": ["auth", "login"]}
                    },
                    "event": [{"listen": "test", "script": {"exec": [
                        "pm.test('Status code is 200', function () { pm.response.to.have.status(200); });",
                        "var jsonData = pm.response.json();",
                        "pm.collectionVariables.set('token', jsonData.access_token);"
                    ]}}]
                },
                {
                    "name": "Login (Error - Wrong Password)",
                    "request": {
                        "method": "POST",
                        "header": [{"key": "Content-Type", "value": "application/x-www-form-urlencoded"}],
                        "body": {
                            "mode": "urlencoded",
                            "urlencoded": [
                                {"key": "username", "value": "admin@gmail.com", "type": "text"},
                                {"key": "password", "value": "wrongpass", "type": "text"}
                            ]
                        },
                        "url": {"raw": "{{base_url}}/auth/login", "host": ["{{base_url}}"], "path": ["auth", "login"]}
                    },
                    "event": [{"listen": "test", "script": {"exec": ["pm.test('Status code is 401', function () { pm.response.to.have.status(401); });"]}}]
                },
                {
                    "name": "Get Me",
                    "request": {
                        "method": "GET",
                        "header": [{"key": "Authorization", "value": "Bearer {{token}}"}],
                        "url": {"raw": "{{base_url}}/auth/me", "host": ["{{base_url}}"], "path": ["auth", "me"]}
                    },
                    "event": [{"listen": "test", "script": {"exec": ["pm.test('Status code is 200', function () { pm.response.to.have.status(200); });"]}}]
                }
            ]
        },
        {
            "name": "2. Courses (Require Admin Token)",
            "item": [
                {
                    "name": "Create Course (Happy Case)",
                    "request": {
                        "method": "POST",
                        "header": [
                            {"key": "Content-Type", "value": "application/json"},
                            {"key": "Authorization", "value": "Bearer {{token}}"}
                        ],
                        "body": {
                            "mode": "raw",
                            "raw": "{\n    \"title\": \"Course Created By Postman\",\n    \"code\": \"POST-{{$randomInt}}\",\n    \"description\": \"Testing create course\"\n}"
                        },
                        "url": {"raw": "{{base_url}}/courses", "host": ["{{base_url}}"], "path": ["courses"]}
                    },
                    "event": [{"listen": "test", "script": {"exec": [
                        "pm.test('Status code is 201 or 409', function () { pm.expect(pm.response.code).to.be.oneOf([201, 409]); });",
                        "if(pm.response.code === 201) { pm.collectionVariables.set('course_id', pm.response.json().id); }"
                    ]}}]
                },
                {
                    "name": "Get All Courses",
                    "request": {
                        "method": "GET",
                        "header": [{"key": "Authorization", "value": "Bearer {{token}}"}],
                        "url": {"raw": "{{base_url}}/courses", "host": ["{{base_url}}"], "path": ["courses"]}
                    },
                    "event": [{"listen": "test", "script": {"exec": ["pm.test('Status code is 200', function () { pm.response.to.have.status(200); });"]}}]
                },
                {
                    "name": "Get Course By ID",
                    "request": {
                        "method": "GET",
                        "header": [{"key": "Authorization", "value": "Bearer {{token}}"}],
                        "url": {"raw": "{{base_url}}/courses/{{course_id}}", "host": ["{{base_url}}"], "path": ["courses", "{{course_id}}"]}
                    },
                    "event": [{"listen": "test", "script": {"exec": ["pm.test('Status code is 200 or 404', function () { pm.expect(pm.response.code).to.be.oneOf([200, 404]); });"]}}]
                },
                {
                    "name": "Update Course",
                    "request": {
                        "method": "PUT",
                        "header": [
                            {"key": "Content-Type", "value": "application/json"},
                            {"key": "Authorization", "value": "Bearer {{token}}"}
                        ],
                        "body": {
                            "mode": "raw",
                            "raw": json.dumps({"title": "Updated Course Title", "description": "Updated by Postman"})
                        },
                        "url": {"raw": "{{base_url}}/courses/{{course_id}}", "host": ["{{base_url}}"], "path": ["courses", "{{course_id}}"]}
                    },
                    "event": [{"listen": "test", "script": {"exec": ["pm.test('Status code is 200 or 404', function () { pm.expect(pm.response.code).to.be.oneOf([200, 404]); });"]}}]
                },
                {
                    "name": "Delete Course",
                    "request": {
                        "method": "DELETE",
                        "header": [{"key": "Authorization", "value": "Bearer {{token}}"}],
                        "url": {"raw": "{{base_url}}/courses/{{course_id}}", "host": ["{{base_url}}"], "path": ["courses", "{{course_id}}"]}
                    },
                    "event": [{"listen": "test", "script": {"exec": ["pm.test('Status code is 200 or 404', function () { pm.expect(pm.response.code).to.be.oneOf([200, 404]); });"]}}]
                }
            ]
        }
    ]
}

output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'docs')
os.makedirs(output_dir, exist_ok=True)
file_path = os.path.join(output_dir, 'EduRAG_Postman_Collection.json')

with open(file_path, 'w', encoding='utf-8') as f:
    json.dump(collection, f, indent=2, ensure_ascii=False)

print(f"Created Postman collection at {file_path}")
