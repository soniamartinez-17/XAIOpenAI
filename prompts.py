# TODO insert file description

def get_system_message():
    system_message = """
    You are a machine-learning model explainer. A model in machine learning is a mathematical representation of a process that can predict or classify outcomes based on input data. It is created through a process called training, where the model learns patterns and relationships from a dataset. 
	Your primary role is to assist with the distillation of essential insights from a machine learning model equation. You will be provided with an equation that is equivalent to the result of applying a dataset to a machine learning algorithm, which results in a new model who has learned and adapted to that data. In other words, which is trained.
	From that equation you will have to extract information in order to make it transparent and understandable to the user. For a formula to be interpretable, it must include several explanations and details that clarify its meaning, the context of its use, and how the different components relate to reality.
    """

    return system_message


# TODO function that generate the prompt
# 8. The explanation should describe how the model reaches that conclusion based on the data we can find in the input. -- for when we have the JSON accessible
def generate_prompt(equation, model, json=""):
    prompt = f""" I am seeking an explanation in order to make the machine learning model identified by the equation '{equation}' compressible and transparent so I can understand it. To give some context the it is a {model} model. The explanation should not be more than 10 lines

	Instructions for explanation:
	1. The explanation should be clear, concise, and understandable to both experts in the field and non-technical users. 
	2. The explanation should give context about how a {model} works
	3. The explanation should cover the definition of all variables in the equation. 
	4. The explanation should specify the units of measurement for all variables, including the variable to be predicted. 
	5. The explanation should cover all relationships that exist between the feature (the independent variables) and the label (the variable to be predicted or dependent variable). That is to say, it should indicate how each of the variables contributes to the rate of change of the label and what the independent term indicates. 
	6. The explanation should indicate what its purpose is (what the equation and label means and what implications the variable to be predicted has). 
	7. The explanation should provide the context in which the formula is applied. For example, if it is used in economics, medicine, physics, biology, etc. 
	8. The explanation should identify the type of model it is (linear regression, logistic regression, decision tree, etc.). 
	9. The explanation should add if the predictive model has logical inconsistencies. For example, highlighting that the model could be wrong if it relates better health to the fact that a person is a smoker.
	10. The explanation should indicate the limitations of the model. 
	11. The explanation, at the end, should generate hypotheses of why these relationships occur in the equation. These should always be marked and labeled as hypotheses, and should also have a notice that these conclusions are hypotheses and must be made by an expert in the field.
    
    With the provided segment and this instructions, proceed with the explanation of the equation {equation}
    """
    return prompt
