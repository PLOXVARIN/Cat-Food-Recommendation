from flask import Flask, render_template, request, redirect, url_for, session
import pandas as pd
import random

app = Flask(__name__)
app.secret_key = 'your_secret_key'
app.jinja_env.globals.update(zip=zip)
app.jinja_env.globals.update(zip=zip)

# ข้อมูลสูตรอาหารแมว
food_data = {
    
    'โปรตีน (g)': [30, 25, 35, 20, 40, 28, 32, 22, 38, 26],
    'ไขมัน (g)': [10, 15, 5, 12, 8, 14, 9, 11, 7, 13],
    'คาร์โบไฮเดรต (g)': [20, 25, 15, 30, 10, 22, 18, 28, 12, 24],
    'ราคา (บาท)': [200, 150, 250, 180, 300, 460, 240, 170, 280, 190]
}
food_df = pd.DataFrame(food_data)

# Fitness Function
def fitness_function(food_recipe, cat_data):
    weights = {
        'โปรตีน': 0.2,
        'ไขมัน': 0.2,
        'คาร์โบไฮเดรต': 0.2,
        'ราคา': 0.1
    }
    protein_score = (food_recipe['โปรตีน (g)'] / cat_data['น้ำหนัก (กก.)']) * weights['โปรตีน']
    fat_score = (food_recipe['ไขมัน (g)'] / cat_data['น้ำหนัก (กก.)']) * weights['ไขมัน']
    carb_score = (food_recipe['คาร์โบไฮเดรต (g)'] / cat_data['น้ำหนัก (กก.)']) * weights['คาร์โบไฮเดรต']
    if food_recipe['ราคา (บาท)'] > cat_data['งบประมาณ (บาท)']:
        price_score = 0
    else:
        price_score = (1 - (food_recipe['ราคา (บาท)'] / cat_data['งบประมาณ (บาท)'])) * weights['ราคา']
    fitness = protein_score + fat_score + carb_score + price_score
    return fitness

# Genetic Algorithm
def genetic_algorithm(food_df, cat_data, population_size=20, generations=10, initial_population=None):
    if initial_population is None:
        population = food_df.sample(n=population_size, replace=True).to_dict('records')
    else:
        population = initial_population
    
    all_generations = []  # เก็บข้อมูลทุกเจน
    best_fitness_overall = -1  # ค่าฟิตเนสที่ดีที่สุด
    best_generation = 0  # เจนที่พบค่าฟิตเนสที่ดีที่สุด
    
    for generation in range(generations):
        fitness_scores = [fitness_function(food, cat_data) for food in population]
        
        # หาค่าฟิตเนสที่ดีที่สุดในเจนนี้
        best_fitness_in_generation = max(fitness_scores)
        if best_fitness_in_generation > best_fitness_overall:
            best_fitness_overall = best_fitness_in_generation
            best_generation = generation + 1
        
        # สร้างประชากรใหม่โดยการเลือกและผสมพันธุ์
        new_population = []
        while len(new_population) < population_size:
            # เลือกพ่อแม่ (Tournament Selection)
            parent1 = max(random.sample(population, 2), key=lambda x: fitness_function(x, cat_data))
            parent2 = max(random.sample(population, 2), key=lambda x: fitness_function(x, cat_data))
            
            # สร้างลูก (Crossover)
            child = {}
            for feature in population[0].keys():
                if random.random() < 0.5:
                    child[feature] = parent1[feature]
                else:
                    child[feature] = parent2[feature]
            
            # Mutation (เพิ่มโอกาสการกลายพันธุ์เป็น 30%)
            if random.random() < 0.3:
                feature_to_mutate = random.choice(list(child.keys()))
                if feature_to_mutate == 'โปรตีน (g)':
                    child[feature_to_mutate] = random.randint(20, 40)
                elif feature_to_mutate == 'ไขมัน (g)':
                    child[feature_to_mutate] = random.randint(5, 15)
                elif feature_to_mutate == 'คาร์โบไฮเดรต (g)':
                    child[feature_to_mutate] = random.randint(10, 30)
                elif feature_to_mutate == 'ราคา (บาท)':
                    child[feature_to_mutate] = random.randint(150, 300)
            
            # เพิ่มลูกเข้าไปในประชากรใหม่
            new_population.append(child)
        
        # อัปเดตประชากร
        population = new_population
        
        # เพิ่มข้อมูลเจนนี้
        all_generations.append({
            'generation': generation + 1,
            'population': population,
            'fitness_scores': [fitness_function(food, cat_data) for food in population],
            'best_fitness_in_generation': best_fitness_in_generation
        })
    
    # เก็บข้อมูลทุกเจนและค่าฟิตเนสที่ดีที่สุดใน session
    session['all_generations'] = all_generations
    session['best_fitness_overall'] = best_fitness_overall
    session['best_generation'] = best_generation
    
    # หาสูตรอาหารที่ดีที่สุด
    best_food = max(population, key=lambda food: fitness_function(food, cat_data))
    best_fitness = fitness_function(best_food, cat_data)
    return best_food, best_fitness
# หน้าแรก
@app.route('/')
def index():
    return render_template('index.html')

# หน้าสร้างรุ่น
@app.route('/create', methods=['GET', 'POST'])
def create():
    if request.method == 'POST':
        cat_data = {
            'อายุ (ปี)': int(request.form['age']),
            'น้ำหนัก (กก.)': float(request.form['weight']),
            'พันธุ์': request.form['breed'],
            'สุขภาพ': request.form['health'],
            'งบประมาณ (บาท)': float(request.form['budget'])
        }
        population_size = int(request.form['population_size'])
        generations = int(request.form['generations'])

        session['cat_data'] = cat_data
        session['population_size'] = population_size
        session['generations'] = generations

        return redirect(url_for('result'))

    return render_template('create.html')

# หน้าแสดงผลลัพธ์
@app.route('/result')
def result():
    if 'cat_data' not in session:
        return redirect(url_for('create'))
    cat_data = session['cat_data']
    population_size = session['population_size']
    generations = session['generations']
    
    initial_population = session.get('current_population', None)
    best_food, best_fitness = genetic_algorithm(food_df, cat_data, population_size, generations, initial_population)
    return render_template('result.html', best_food=best_food, best_fitness=best_fitness)

# หน้าแสดงข้อมูลฟิตเนส
@app.route('/fitness_data')
def fitness_data():
    if 'all_generations' not in session:
        return redirect(url_for('create'))  # ถ้าไม่มีข้อมูล ให้กลับไปที่หน้า create
    all_generations = session['all_generations']
    return render_template('fitness_data.html', all_generations=all_generations)

if __name__ == '__main__':
    app.run(debug=True)