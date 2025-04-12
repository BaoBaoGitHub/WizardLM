base_template = """Please optimize the given Java programming test question by increasing its difficulty slightly. After optimizing the question, provide the corresponding Java code for the optimized question.

You can increase the difficulty using, but not limited to, the following methods: 
{method}

Original question:
{question}

Optimized question and its Java code answer:"""


def constraints(question):
    method = "Add new constraints and requirements to the original problem, adding approximately 10 additional words."
    return base_template.format(method=method, question=question)

def less_common(question):
    method = "Replace a commonly used requirement in the programming task with a less common and more specific one."
    return base_template.format(method=method, question=question)

def reasoning(question):
    method = "If the original problem can be solved with only a few logical steps, please add more reasoning steps."
    return base_template.format(method=method, question=question)

def erroneous(question):
    method = "Provide a piece of erroneous code as a reference to increase misdirection."
    return base_template.format(method=method, question=question)

def time_space_complexity(question):
    method = "Use excellent data structures and algorithms to optimize the time and space complexity of your code."
    return base_template.format(method=method, question=question)

def oo(question):
    method = "Take advantage of object-oriented features, such as encapsulation inheritance and polymorphism, while requiring improved code robustness."
    return base_template.format(method=method, question=question)

def design_pattern(question):
    method = "Use design patterns that are commonly used in this type of problem."
    return base_template.format(method=method, question=question)

