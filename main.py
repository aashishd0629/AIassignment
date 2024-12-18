from flask import Flask, request, render_template, redirect, url_for
from owlready2 import get_ontology, Thing, DatatypeProperty, ObjectProperty
import random

app = Flask(__name__)

#load ontology
ontology_path = "temponto.owl"
onto = get_ontology(ontology_path).load()


onto = get_ontology(ontology_path).load()
print(list(onto.classes()))



# Define the Student and related classes 
with onto:
    class Student(Thing):
        pass

    class name(DatatypeProperty):
        domain = [Student]
        range = [str]

    # Define temperature-related classes
    class Temperature(Thing):
        pass

    class Celsius(Temperature):
        pass

    class Fahrenheit(Temperature):
        pass

    class Kelvin(Temperature):
        pass

    # Conversion classes
    class Conversion(Thing):
        pass

    class ToCelsius(Conversion):
        pass

    class ToFahrenheit(Conversion):
        pass

    class ToKelvin(Conversion):
        pass

    # History class to store results
    class History(Thing):
        pass

    # Quote class for random quotes
    class Quote(Thing):
        pass

    class content(DatatypeProperty):
        domain = [Quote]
        range = [str]

    # Property for conversion
    class performsConversion(ObjectProperty):
        domain = [Student]
        range = [Conversion]

    class actsOnTemperature(ObjectProperty):
        domain = [Conversion]
        range = [Temperature]

    class generatesResult(ObjectProperty):
        domain = [Conversion]
        range = [History]

# Function to perform temperature conversion
def convert_temperature(value, from_unit, to_unit):
    """Performs temperature conversion and returns the result"""
    if from_unit == "Celsius":
        if to_unit == "Fahrenheit":
            return value * 9/5 + 32
        elif to_unit == "Kelvin":
            return value + 273.15
    elif from_unit == "Fahrenheit":
        if to_unit == "Celsius":
            return (value - 32) * 5/9
        elif to_unit == "Kelvin":
            return (value - 32) * 5/9 + 273.15
    elif from_unit == "Kelvin":
        if to_unit == "Celsius":
            return value - 273.15
        elif to_unit == "Fahrenheit":
            return (value - 273.15) * 9/5 + 32
    return None



# Function to get a random quote
def get_random_quote():
    """Selects a random quote from the Quote class"""
    quotes = list(onto.Quote.instances())
    print(quotes)
    if quotes:
        random_quote = random.choice(quotes)
        return random_quote.content if random_quote.content else "No quote available."
    return "No quote available."

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        # Add new student to the ontology
        student_name = request.form.get("student_name")
        if student_name:
            with onto:
                new_student = Student()
                new_student.name = student_name
                print(f"Created new student: {student_name}")  # Check if the student is being created
                onto.save(file=ontology_path, format="rdfxml")
                return redirect(url_for("index"))

    # Fetch all students
    students = list(onto.Student.instances())
    return render_template("index.html", students=students, conversion_result=None, quote=None)

@app.route("/convert_temperature", methods=["POST"])
def convert_temperature_route():
    temperature_value = float(request.form.get("temperature_value"))
    from_unit = request.form.get("from_unit")
    to_unit = request.form.get("to_unit")

    # Perform the temperature conversion
    converted_value = convert_temperature(temperature_value, from_unit, to_unit)

    # Create History instance with the result
    if converted_value is not None:
        with onto:
            history_instance = History()
            history_instance.result = converted_value
            history_instance.temperature_unit = to_unit
            onto.save(file=ontology_path, format="rdfxml")

        # Generate random quote
        quote = get_random_quote()
        return render_template("index.html", conversion_result=converted_value, quote=quote, students=list(onto.Student.instances()))

    return render_template("index.html", conversion_result="Invalid conversion", quote=None, students=list(onto.Student.instances()))

if __name__ == "__main__":
    app.run(debug=True)
