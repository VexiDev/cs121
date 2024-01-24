import benguin

benguin.benguin()

#arithmetic expression interpreter and solver
def arithmetic_interpreter(expression) -> str:

    #catch any errors that may occur while evaluating the expression
    try:
    
        #get list of alphabetical variables in expression and remove duplicates
        variables = list(set([variable for variable in expression.replace(" ", "") if variable.isalpha()]))
    
        # loop through each  variable found
        for variable in variables:
    
            # replace each variable with user input
            expression = expression.replace(variable, input(f"Enter a value for {variable}: "))
    
        #print result
        print(f"The solution for your expression is {eval(expression):.2f}\n")
    
    #If a syntax error is found in the expression, print a red error message
    except SyntaxError:
        print("\033[31mThere is a syntax error in your expression, please review your syntax and try again.\033[0m\n")
    
    #If any other error is raised, print a general error message
    except:
        print("\033[31mThere was an error while evaluating your expression, please try again.\033[0m\n")

# if the file is run directly, run the arthmetic interpreter
if __name__ == "__main__":
    arithmetic_interpreter(input("Enter an arithmetic expression (include all operators): "))