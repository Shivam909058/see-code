# test.py
# Intentionally vulnerable and low-quality Python code for testing analysis tools.
# DO NOT use this in production.

import os
import sys
import random
import time
import math
import hashlib
import json
import sqlite3
import requests   # unused import
from datetime import datetime   # unused import


# Hardcoded secrets (Security Issue)
DB_PASSWORD = "super_secret_password"
API_TOKEN = "abcd1234"

# Global mutable state (Bad Practice)
cache = {}

# SQL Injection Example (Security Issue)
def get_user_data(username):
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    # vulnerable query
    query = "SELECT * FROM users WHERE username = '" + username + "';"
    cursor.execute(query)
    data = cursor.fetchall()
    conn.close()
    return data

# Dangerous eval/exec usage (Security Issue)
def run_code(code_str):
    return eval(code_str)

def run_script(script):
    exec(script)

# Code duplication (Duplication Issue)
def calculate_area_rectangle(w, h):
    return w * h

def calculate_area_rectangle_copy(w, h):
    return w * h   # duplicate

# Inefficient performance (nested loops & string concatenation in loop)
def slow_string_builder(n):
    result = ""
    for i in range(n):
        for j in range(1000):
            result += str(i * j)
    return result

# Complexity: deeply nested conditionals
def complex_logic(x, y, z):
    if x > 10:
        if y > 5:
            if z > 3:
                if x % 2 == 0:
                    if y % 2 == 0:
                        return "Case A"
                    else:
                        return "Case B"
                else:
                    if z % 2 == 0:
                        return "Case C"
                    else:
                        return "Case D"
            else:
                if x > y:
                    return "Case E"
                else:
                    return "Case F"
        else:
            if z > x:
                return "Case G"
            else:
                return "Case H"
    else:
        if y < 0:
            if z < 0:
                return "Negative"
            else:
                return "Mixed"
        else:
            return "Small values"

# Long function (>50 lines) without modularization
def big_function(data):
    total = 0
    for i in range(len(data)):
        total += data[i]
    for i in range(1000):
        total += i
    for j in range(500):
        total -= j
    for k in range(200):
        total += k * 2
    for x in range(300):
        total += x ** 2
    for y in range(400):
        total += y % 5
    for z in range(600):
        total -= z // 3
    for a in range(700):
        total += a * 3
    for b in range(800):
        total -= b % 7
    for c in range(900):
        total += c // 2
    for d in range(1000):
        total += d * d
    return total

# Function with too many parameters (bad design)
def bad_design(a, b, c, d, e, f, g, h, i, j, k, l):
    return (a + b + c + d + e + f + g + h + i + j + k + l)

# Missing error handling
def divide_numbers(x, y):
    return x / y   # crash on division by zero

# Unused variables
def unused_vars():
    a = 10
    b = 20
    c = a + b
    return 42

# Hardcoded file paths
def read_secret_file():
    with open("/etc/passwd", "r") as f:
        return f.read()

# Infinite loop (bug/performance issue)
def bad_loop():
    while True:
        print("Running...")   # will never stop

# Copy-pasted duplicate blocks
def duplicate1():
    s = 0
    for i in range(10):
        s += i
    return s

def duplicate2():
    s = 0
    for i in range(10):
        s += i
    return s

# Function with no docstring
def undocumented(a, b):
    return a * b

# Poor naming convention
def XYZFunction(x, Y, zzz):
    return x + Y + zzz

# Deprecated functions usage (bad practice)
def old_hash(data):
    return hashlib.md5(data.encode()).hexdigest()

# Overly broad exception handling
def bad_try():
    try:
        x = 1 / 0
    except:
        pass

# Functions with side effects (hidden)
def hidden_side_effects(lst=[]):
    lst.append(1)
    return lst

# Duplicate logic in multiple places
def is_even(n):
    return n % 2 == 0

def is_even_copy(n):
    return n % 2 == 0

# Random sleep (performance anti-pattern)
def random_sleep():
    time.sleep(random.randint(1, 5))
    return "done"

# Function that mixes responsibilities (SRP violation)
def mixed_responsibility(user, filename):
    print("Saving user:", user)
    with open(filename, "w") as f:
        f.write(str(user))
    print("Notification sent!")

# Poorly documented class with bad design
class BadClass:
    def __init__(self, a, b, c, d, e):
        self.a = a
        self.b = b
        self.c = c
        self.d = d
        self.e = e

    def method1(self):
        return self.a + self.b

    def method2(self):
        return self.b + self.c

    def method3(self):
        return self.c + self.d

    def method4(self):
        return self.d + self.e

    def method5(self):
        return self.e + self.a

# Giant class with many unrelated methods (God class anti-pattern)
class GodClass:
    def add(self, a, b): return a + b
    def sub(self, a, b): return a - b
    def mul(self, a, b): return a * b
    def div(self, a, b): return a / b
    def log(self, msg): print(msg)
    def save_file(self, name, content): open(name, "w").write(content)
    def load_file(self, name): return open(name).read()
    def net_request(self, url): return requests.get(url).text
    def cache_add(self, key, val): cache[key] = val
    def cache_get(self, key): return cache.get(key)
    def bad_sql(self, q): 
        conn = sqlite3.connect("data.db")
        cur = conn.cursor()
        cur.execute(q)   # SQL injection risk
        return cur.fetchall()
