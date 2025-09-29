from flask import Flask, render_template, request
import pickle
import numpy as np
import pandas as pd

app = Flask(__name__)

# --- CORRECTED CODE BLOCK ---
try:
    similarity = pickle.load(open('models/similarity.pkl', 'rb'))
    
    # We load the list of dictionaries from courses.pkl
    courses_list = pickle.load(open('models/courses.pkl', 'rb'))
    # THEN, we convert that list into a pandas DataFrame
    courses_df = pd.DataFrame(courses_list)

    # We load the list of course names from course_list.pkl
    course_names = pickle.load(open('models/course_list.pkl', 'rb'))

except FileNotFoundError:
    print("Error: One or more model files not found. Make sure 'models/similarity.pkl', 'models/courses.pkl', and 'models/course_list.pkl' exist.")
    exit()
except Exception as e:
    print(f"Error loading model files: {e}")
    exit()

# This line now works correctly because courses_df is a DataFrame
course_url_dict = courses_df.set_index('course_name')['course_url'].to_dict()

def recommend(course_name):
    """
    Recommends courses similar to the one provided.
    """
    if course_name not in courses_df['course_name'].values:
        return []

    try:
        # Get the index of the course that matches the course name
        index = courses_df[courses_df['course_name'] == course_name].index[0]
        
        # Get the list of cosine similarity scores for that course
        distances = sorted(list(enumerate(similarity[index])), reverse=True, key=lambda x: x[1])
        
        recommended_courses = []
        # Get the top 6 most similar courses (index 0 is the course itself)
        for i in distances[1:7]:
            recommended_name = courses_df.iloc[i[0]].course_name
            recommended_url = courses_df.iloc[i[0]].course_url
            recommended_courses.append({'name': recommended_name, 'url': recommended_url})
            
        return recommended_courses
    except IndexError:
        # This handles cases where the course name might exist but causes an indexing error
        return []
    except Exception as e:
        print(f"Error during recommendation: {e}")
        return []

@app.route('/', methods=['GET', 'POST'])
def index():
    recommended_courses = []
    selected_course = None
    
    if request.method == 'POST':
        selected_course = request.form['course_name']
        recommended_courses = recommend(selected_course)
        
    return render_template('index.html', courses=course_names, recommendations=recommended_courses, selected_course=selected_course)

if __name__ == '__main__':
    app.run(debug=True)