import pandas as pd
import random
from tabulate import tabulate

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
def genetic_algorithm(food_df, cat_data, population_size=20, generations=10):
    population = food_df.sample(n=population_size, replace=True).to_dict('records')
    all_generations = []
    best_fitness_overall = -1
    best_generation = 0

    for generation in range(generations):
        fitness_scores = [fitness_function(food, cat_data) for food in population]
        
        best_fitness_in_generation = max(fitness_scores)
        if best_fitness_in_generation > best_fitness_overall:
            best_fitness_overall = best_fitness_in_generation
            best_generation = generation + 1

        new_population = []
        while len(new_population) < population_size:
            parent1 = max(random.sample(population, 2), key=lambda x: fitness_function(x, cat_data))
            parent2 = max(random.sample(population, 2), key=lambda x: fitness_function(x, cat_data))
            
            child = {}
            for feature in population[0].keys():
                child[feature] = parent1[feature] if random.random() < 0.5 else parent2[feature]

            if random.random() < 0.3:
                feature_to_mutate = random.choice(list(child.keys()))
                ranges = {
                    'โปรตีน (g)': (20, 40),
                    'ไขมัน (g)': (5, 15),
                    'คาร์โบไฮเดรต (g)': (10, 30),
                    'ราคา (บาท)': (150, 300)
                }
                child[feature_to_mutate] = random.randint(*ranges[feature_to_mutate])

            new_population.append(child)

        population = new_population
        all_generations.append({
            'generation': generation + 1,
            'best_fitness': best_fitness_in_generation,
            'population': population.copy(),
            'fitness_scores': fitness_scores.copy()
        })

    best_food = max(population, key=lambda food: fitness_function(food, cat_data))
    return best_food, best_fitness_overall, all_generations, best_generation

def get_user_input():
    print("=== กรุณากรอกข้อมูลแมวของคุณ ===")
    cat_data = {
        'อายุ (ปี)': int(input("อายุแมว (ปี): ")),
        'น้ำหนัก (กก.)': float(input("น้ำหนักแมว (กก.): ")),              
        'งบประมาณ (บาท)': float(input("งบประมาณ (บาท): "))
    }
    
    population_size = int(input("\nขนาดประชากรเริ่มต้น (แนะนำ 20): "))
    generations = int(input("จำนวนรุ่นที่ต้องการพัฒนา (แนะนำ 10): "))
    
    return cat_data, population_size, generations

def display_results(best_food, best_fitness, all_generations, best_generation):
    print("\n=== ผลลัพธ์สูตรอาหารที่ดีที่สุด ===")
    print(f"โปรตีน: {best_food['โปรตีน (g)']} g")
    print(f"ไขมัน: {best_food['ไขมัน (g)']} g")
    print(f"คาร์โบไฮเดรต: {best_food['คาร์โบไฮเดรต (g)']} g")
    print(f"ราคา: {best_food['ราคา (บาท)']} บาท")
    print(f"\nคะแนนฟิตเนส: {best_fitness:.2f}")
    print(f"รุ่นที่ดีที่สุด: รุ่นที่ {best_generation}")

    if input("\nต้องการดูข้อมูลฟิตเนสทั้งหมดทุกรุ่นหรือไม่? (y/n): ").lower() == 'y':
        print("\n=== ข้อมูลฟิตเนสทุกรุ่น ===")
        table_data = []
        for gen in all_generations:
            table_data.append([
                gen['generation'],
                f"{max(gen['fitness_scores']):.2f}",
                f"{sum(gen['fitness_scores'])/len(gen['fitness_scores']):.2f}",
                f"{min(gen['fitness_scores']):.2f}"
            ])
        
        print(tabulate(table_data, 
                     headers=["รุ่น", "ฟิตเนสสูงสุด", "ฟิตเนสเฉลี่ย", "ฟิตเนสต่ำสุด"],
                     tablefmt="grid"))
        if input("\nต้องการดูข้อมูลประชากรทุกรุ่นอย่างละเอียดหรือไม่? (y/n): ").lower() == 'y':
            print("\n=== ข้อมูลประชากรทุกรุ่น ===")
        for gen in all_generations:
            print(f"\n• Generation {gen['generation']}:")
            
            # สร้างข้อมูลสำหรับตาราง
            table_data = []
            for idx, (ind, score) in enumerate(zip(gen['population'], gen['fitness_scores'])):
                table_data.append([
                    idx+1,
                    ind['โปรตีน (g)'],
                    ind['ไขมัน (g)'],
                    ind['คาร์โบไฮเดรต (g)'],
                    ind['ราคา (บาท)'],
                    round(score, 2)
                ])
            
            # พิมพ์ตารางด้วยรูปแบบสวยงาม
            print(tabulate(
                table_data,
                headers=[
                    "ลำดับ", "โปรตีน (g)", "ไขมัน (g)", 
                    "คาร์โบไฮเดรต (g)", "ราคา (บาท)", "Fitness"
                ],
                tablefmt="grid",
                numalign="center",
                stralign="center"
            ))
            
            # แสดงค่าสถิติเสริม
            print(f"\nสถิติรุ่นนี้:")
            print(f"- Fitness สูงสุด: {max(gen['fitness_scores']):.2f}")
            print(f"- Fitness ต่ำสุด: {min(gen['fitness_scores']):.2f}")
            
            if input("\nกด Enter เพื่อดูรุ่นถัดไป หรือพิมพ์ 'q' เพื่อออก: ").lower() == 'q':
                break


def main():
    cat_data, population_size, generations = get_user_input()
    best_food, best_fitness, all_generations, best_gen = genetic_algorithm(
        food_df, cat_data, population_size, generations
    )
    display_results(best_food, best_fitness, all_generations, best_gen)

if __name__ == "__main__":
    main()