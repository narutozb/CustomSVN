import os

def delete_migration_files(project_dir):
    for root, dirs, files in os.walk(project_dir):
        if 'migrations' in dirs:
            migration_dir = os.path.join(root, 'migrations')
            for file_name in os.listdir(migration_dir):
                if file_name != '__init__.py' and file_name.endswith('.py'):
                    file_path = os.path.join(migration_dir, file_name)
                    try:
                        os.remove(file_path)
                        print(f"Deleted: {file_path}")
                    except Exception as e:
                        print(f"Error deleting {file_path}: {e}")

if __name__ == "__main__":
    project_directory = input("Enter the path to your Django project: ")
    delete_migration_files(project_directory)
