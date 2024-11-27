from flask import Blueprint, render_template, request, redirect, url_for, current_app, flash
import json
import os
from werkzeug.utils import secure_filename

# Initialize Blueprint
tastenest = Blueprint('tastenest', __name__)

# Path to load files
recipes_file = "data/recipes.json"
groceries_file = "data/groceries.json"
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])

# Load data functions
def load_recipes():
    try:
        with open(recipes_file, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return []

def load_groceries():
    try:
        with open(groceries_file, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return []

# Save data functions
def save_file(file_path, new_data):
    with open(file_path, 'w') as f:
        json.dump(new_data, f, indent=4)

# Function to check allowed file extensions
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Function to generate new ID for recipes
def make_id_number_for_recipes():
    recipes = load_recipes()
    if not recipes:
        return 1
    return max(recipe['id'] for recipe in recipes) + 1

def make_id_number_for_groceries():
    groceries = load_groceries()
    if not groceries:
        return 1
    return max(grocery['id'] for grocery in groceries) + 1

@tastenest.route("/")
def start():
    return redirect(url_for('tastenest.home'))

# Routes for different pages
@tastenest.route('/home')
def home():
    items = load_recipes()
    return render_template('index.html', items=items)

@tastenest.route('/favourites')
def favourites():
    items = load_recipes()
    return render_template('favourites.html', items=items)

@tastenest.route('/groceries')
def groceries():
    items = load_groceries()
    return render_template('groceries.html', items=items)

@tastenest.route('/add-to-groceries/<int:recipe_id>', methods=['POST'])
def add_to_groceries(recipe_id):
    recipes = load_recipes()
    recipe = next((item for item in recipes if item['id'] == recipe_id), None)
    if not recipe:
        flash('Recipe not found!')
        return redirect(url_for('tastenest.recipe_details', recipe_id=recipe_id))

    # Check if "Add to groceries" button is clicked
    add_to_groceries = request.form.get('add_to_groceries')
    
    if add_to_groceries:  # If the button is clicked
        groceries = load_groceries()
        
        # Format ingredients with default checked = False
        grocery_items = [
            {"name": ingredient, "checked": False}
            for ingredient in recipe['ingredients']
        ]
        
        # Add the recipe's ingredients to the groceries list
        groceries.append({
            "id": make_id_number_for_groceries(),
            "title": recipe['title'],
            "ingredients": grocery_items
        })
        
        save_file(groceries_file, groceries)
        flash(f"Ingredients from '{recipe['title']}' added to your groceries!")
    
    return redirect(url_for('tastenest.recipe_details', recipe_id=recipe_id))

@tastenest.route('/delete-grocery-list/<int:grocery_id>', methods=['GET','POST'])
def delete_grocery_list(grocery_id):
    groceries = load_groceries()

    # Find the grocery list with the matching ID
    grocery_to_delete = next((grocery for grocery in groceries if grocery['id'] == grocery_id), None)
    
    if request.method == 'POST':
        if not grocery_to_delete:
            flash("Grocery list not found.")
            return redirect(url_for('tastenest.groceries'))

        # Remove the matched grocery list
        groceries.remove(grocery_to_delete)

        # Save the updated groceries list
        save_file(groceries_file, groceries)
        
        flash(f"'{grocery_to_delete['title']}' grocery list deleted successfully!")
        return redirect(url_for('tastenest.groceries'))
    return render_template('delete-list.html', grocery=grocery_to_delete, grocery_id=grocery_id)


@tastenest.route('/toggle-ingredient/<int:grocery_id>/<string:ingredient_name>', methods=['POST'])
def toggle_ingredient(grocery_id, ingredient_name):
    groceries = load_groceries()

    # Find the grocery list by its ID
    grocery_list = next((item for item in groceries if item['id'] == grocery_id), None)
    if not grocery_list:
        flash("Grocery list not found.")
        return redirect(url_for('tastenest.groceries'))

    # Find the ingredient to toggle by name
    for ingredient in grocery_list['ingredients']:
        if ingredient['name'] == ingredient_name:
            # Toggle the checked status
            ingredient['checked'] = not ingredient['checked']
            break

    # Save the updated groceries list
    save_file(groceries_file, groceries)

    return redirect(url_for('tastenest.groceries'))

@tastenest.route('/toggle-favourite/<int:recipe_id>', methods=['POST'])
def toggle_favourite(recipe_id):
    recipes = load_recipes()
    recipe = next((item for item in recipes if item['id'] == recipe_id), None)
    if recipe:
        # Toggle the 'favourited' status
        recipe['favourited'] = not recipe.get('favourited', False)
        save_file(recipes_file, recipes)
        flash(f"{'Added to' if recipe['favourited'] else 'Removed from'} favourites.")
    else:
        flash("Recipe not found.")
    return redirect(url_for('tastenest.recipes'))

@tastenest.route('/recipes', methods=['GET', 'POST']) # ADD IS IN HERE
def recipes():
    if request.method == 'POST':
        # Extract form data
        title = request.form['title']
        ingredients = request.form['ingredients'].split(',')
        instructions = request.form['instructions']
        description = request.form['description']

        # Handle time as a dict for hrs and minutes
        try:
            hrs = int(request.form['hrs'])
            minutes = int(request.form['minutes'])
            time = {"hrs": hrs, "minutes": minutes}
        except (ValueError, KeyError):
            flash('Invalid time input. Please enter valid hours and minutes.')
            return redirect(url_for('tastenest.add_recipes'))

        # Handle image upload
        image = request.files['image']
        if image and allowed_file(image.filename):
            filename = secure_filename(image.filename)
            image.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))
        else:
            flash('Invalid image file or no image uploaded.')
            return redirect(url_for('tastenest.add_recipes'))

        # Create a new recipe entry
        recipes = load_recipes()
        new_recipe = {
            'id': make_id_number_for_recipes(),
            'title': title,
            'ingredients': ingredients,
            'instructions': instructions,
            'description': description,
            'image': filename,  # Store the image filename
            'time': time,
            'featured': False,
            'favourited': False,
            'rating': None
        }
        recipes.append(new_recipe)
        save_file(recipes_file, recipes)
        flash('Recipe added successfully with image!')
        return redirect(url_for('tastenest.recipes'))

    # If GET request, load recipes and display them
    recipes = load_recipes()
    return render_template('recipes.html', items=recipes)

@tastenest.route('/recipe-details/<int:recipe_id>', methods=['GET', 'POST']) # EDIT IS IN HERE
def recipe_details(recipe_id):
    recipes = load_recipes()
    recipe = next((recipe for recipe in recipes if recipe['id'] == recipe_id), None)

    if request.method == 'POST':
        recipe['title'] = request.form.get('title', recipe['title'])
        recipe['description'] = request.form.get('description', recipe['description'])
        recipe['ingredients'] = [ingredient.strip() for ingredient in request.form.get('ingredients', ','.join(recipe['ingredients'])).split(',')]
        recipe['instructions'] = request.form.get('instructions', recipe['instructions'])
        
        # Handle time as a dict for hrs and minutes
        try:
            hrs = int(request.form['hrs'])
            minutes = int(request.form['minutes'])
            recipe['time'] = {"hrs": hrs, "minutes": minutes}
        except (ValueError, KeyError):
            flash('Invalid time input. Please enter valid hours and minutes.')
            return redirect(request.url)

        # Handle image upload/update
        image = request.files['image']
        if image and allowed_file(image.filename):

            # Delete old image if it exists
            old_image_path = os.path.join(current_app.config['UPLOAD_FOLDER'], recipe['image'])
            if os.path.exists(old_image_path):
                os.remove(old_image_path)

            # Save new image
            filename = secure_filename(image.filename)
            image.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))  # Use current_app.config
            recipe['image'] = filename  # Update the image filename

        save_file(recipes_file, recipes)
        flash('Recipe updated successfully with new image (if applicable).')
        return redirect(url_for('tastenest.recipe_details', recipe_id=recipe['id']))
    
    if recipe is None:
        return "Recipe not found", 404
    
    return render_template('recipe-details.html', recipe=recipe)

@tastenest.route('/dismiss-flash', methods=['POST'])
def dismiss_flash():
    # Get the referrer URL from the form data
    referrer = request.form.get('referrer')
    
    # Redirect back to the referrer or a default page if not available
    return redirect(referrer or url_for('tastenest.home'))

@tastenest.route('/delete-recipe/<int:recipe_id>', methods=['GET', 'POST'])
def delete_recipe(recipe_id):
    recipes = load_recipes()
    recipe = next((recipe for recipe in recipes if recipe['id'] == recipe_id), None)
    if not recipe:
        return "Recipe not found", 404

    if request.method == 'POST':
        if recipe['image']:
            image_path = os.path.join(current_app.config['UPLOAD_FOLDER'], recipe['image'])
            if os.path.exists(image_path):
                os.remove(image_path)

        recipes.remove(recipe)
        save_file(recipes_file, recipes)
        flash('Recipe and its image deleted successfully!')
        return redirect(url_for('tastenest.recipes'))

    return render_template('delete.html', recipe=recipe)

