from llm_helper import generate_glossary_definition, generate_image_description

print("Testing glossary definition generation...")
print("-" * 50)

definition = generate_glossary_definition("API", "Application Programming Interface")
print(f"API(Application Programming Interface)")
print(f"Definition: {definition}")

print("\nTesting image description generation...")
print("-" * 50)

description = generate_image_description(
    "The following screenshot shows the login page of the application."
)
print(f"Caption: {description}")