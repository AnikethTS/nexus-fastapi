from pathlib import Path
import json
from typing import Dict, List, Any, Optional
from datetime import datetime

DEFAULT_LAYOUT = {
    "app": ["routers", "models", "schemas", "crud"],
    "core": ["database", "config", "security"],
    "tests": [],
    "infra": []
}

class FastAPIGenerator:
    def __init__(self, project_name: str, config: Optional[Dict[str, Any]] = None):
        self.project_name = project_name
        self.config = config or {
            "project_name": project_name,
            "description": "FastAPI application",
            "version": "1.0.0",
            "apps": []
        }
        self.base_path = Path(project_name)
        
    def create_directory_structure(self):
        """Create the basic directory structure"""
        directories = [
            self.base_path,
            self.base_path / "apps",
            self.base_path / "core",
            self.base_path / "core" / "database",
            self.base_path / "core" / "config",
            self.base_path / "core" / "security",
            self.base_path / "tests",
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
            
        # Create __init__.py files
        init_files = [
            self.base_path / "__init__.py",
            self.base_path / "apps" / "__init__.py",
            self.base_path / "core" / "__init__.py",
            self.base_path / "core" / "database" / "__init__.py",
            self.base_path / "core" / "config" / "__init__.py",
            self.base_path / "core" / "security" / "__init__.py",
            self.base_path / "tests" / "__init__.py",
        ]
        
        for init_file in init_files:
            init_file.touch()

    def get_sqlalchemy_type(self, field_type: str) -> str:
        """Convert field type to SQLAlchemy type"""
        type_mapping = {
            'string': 'String',
            'integer': 'Integer',
            'float': 'Float',
            'boolean': 'Boolean',
            'datetime': 'DateTime',
            'text': 'Text',
            'json': 'JSON'
        }
        return type_mapping.get(field_type.lower(), 'String')

    def get_python_type(self, field_type: str) -> str:
        """Convert field type to Python type"""
        type_mapping = {
            'string': 'str',
            'integer': 'int',
            'float': 'float',
            'boolean': 'bool',
            'datetime': 'datetime',
            'text': 'str',
            'json': 'dict'
        }
        return type_mapping.get(field_type.lower(), 'str')

    def generate_model(self, app_name: str, model_config: Dict[str, Any]):
        """Generate SQLAlchemy model"""
        model_name = model_config['name']
        fields = model_config['fields']
        
        imports = set(['Column', 'Integer', 'DateTime'])
        model_content = f'''from sqlalchemy import {', '.join(sorted(imports))}
from core.database.base import Base
from datetime import datetime

class {model_name}(Base):
    __tablename__ = "{model_name.lower()}s"
    
    id = Column(Integer, primary_key=True, index=True)
'''
        
        for field in fields:
            field_name = field['name']
            field_type = self.get_sqlalchemy_type(field['type'])
            nullable = field.get('nullable', True)
            default = field.get('default')
            
            column_def = f"    {field_name} = Column({field_type}"
            
            if not nullable:
                column_def += ", nullable=False"
            
            if default is not None:
                if isinstance(default, str):
                    column_def += f', default="{default}"'
                else:
                    column_def += f', default={default}'
            
            column_def += ")\n"
            model_content += column_def
        
        return model_content

    def generate_schema(self, model_config: Dict[str, Any]):
        """Generate Pydantic schemas"""
        model_name = model_config['name']
        fields = model_config['fields']
        
        schema_content = '''from pydantic import BaseModel
from typing import Optional
from datetime import datetime

'''
        
        # Base schema
        schema_content += f'''class {model_name}Base(BaseModel):
'''
        for field in fields:
            field_name = field['name']
            field_type = self.get_python_type(field['type'])
            nullable = field.get('nullable', True)
            
            if nullable:
                schema_content += f"    {field_name}: Optional[{field_type}] = None\n"
            else:
                schema_content += f"    {field_name}: {field_type}\n"
        
        # Create schema
        schema_content += f'''

class {model_name}Create({model_name}Base):
    pass

class {model_name}Update({model_name}Base):
    pass

class {model_name}Response({model_name}Base):
    id: int
    
    class Config:
        from_attributes = True
'''
        
        return schema_content

    def generate_crud(self, model_config: Dict[str, Any]):
        """Generate CRUD operations"""
        model_name = model_config['name']
        
        crud_content = f'''from sqlalchemy.orm import Session
from typing import List, Optional
from .models import {model_name}
from .schemas import {model_name}Create, {model_name}Update

class {model_name}CRUD:
    def create(self, db: Session, obj_in: {model_name}Create) -> {model_name}:
        db_obj = {model_name}(**obj_in.model_dump())
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def get(self, db: Session, id: int) -> Optional[{model_name}]:
        return db.query({model_name}).filter({model_name}.id == id).first()
    
    def get_multi(self, db: Session, skip: int = 0, limit: int = 100) -> List[{model_name}]:
        return db.query({model_name}).offset(skip).limit(limit).all()
    
    def update(self, db: Session, db_obj: {model_name}, obj_in: {model_name}Update) -> {model_name}:
        update_data = obj_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def delete(self, db: Session, id: int) -> {model_name}:
        obj = db.query({model_name}).get(id)
        db.delete(obj)
        db.commit()
        return obj

{model_name.lower()}_crud = {model_name}CRUD()
'''
        
        return crud_content

    def generate_service(self, model_config: Dict[str, Any]):
        """Generate service layer"""
        model_name = model_config['name']
        
        service_content = f'''from sqlalchemy.orm import Session
from typing import List, Optional
from .crud import {model_name.lower()}_crud
from .schemas import {model_name}Create, {model_name}Update, {model_name}Response

class {model_name}Service:
    def create_{model_name.lower()}(self, db: Session, obj_in: {model_name}Create) -> {model_name}Response:
        return {model_name.lower()}_crud.create(db=db, obj_in=obj_in)
    
    def get_{model_name.lower()}(self, db: Session, id: int) -> Optional[{model_name}Response]:
        return {model_name.lower()}_crud.get(db=db, id=id)
    
    def get_{model_name.lower()}s(self, db: Session, skip: int = 0, limit: int = 100) -> List[{model_name}Response]:
        return {model_name.lower()}_crud.get_multi(db=db, skip=skip, limit=limit)
    
    def update_{model_name.lower()}(self, db: Session, id: int, obj_in: {model_name}Update) -> Optional[{model_name}Response]:
        db_obj = {model_name.lower()}_crud.get(db=db, id=id)
        if not db_obj:
            return None
        return {model_name.lower()}_crud.update(db=db, db_obj=db_obj, obj_in=obj_in)
    
    def delete_{model_name.lower()}(self, db: Session, id: int) -> Optional[{model_name}Response]:
        return {model_name.lower()}_crud.delete(db=db, id=id)

{model_name.lower()}_service = {model_name}Service()
'''
        
        return service_content

    def generate_routes(self, model_config: Dict[str, Any]):
        """Generate FastAPI routes"""
        model_name = model_config['name']
        model_lower = model_name.lower()
        
        routes_content = f'''from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from core.database.base import get_db
from .schemas import {model_name}Create, {model_name}Update, {model_name}Response
from .service import {model_lower}_service

router = APIRouter()

@router.post("/", response_model={model_name}Response)
def create_{model_lower}({model_lower}: {model_name}Create, db: Session = Depends(get_db)):
    return {model_lower}_service.create_{model_lower}(db=db, obj_in={model_lower})

@router.get("/", response_model=List[{model_name}Response])
def read_{model_lower}s(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return {model_lower}_service.get_{model_lower}s(db=db, skip=skip, limit=limit)

@router.get("/{{id}}", response_model={model_name}Response)
def read_{model_lower}(id: int, db: Session = Depends(get_db)):
    db_{model_lower} = {model_lower}_service.get_{model_lower}(db=db, id=id)
    if db_{model_lower} is None:
        raise HTTPException(status_code=404, detail="{model_name} not found")
    return db_{model_lower}

@router.put("/{{id}}", response_model={model_name}Response)
def update_{model_lower}(id: int, {model_lower}: {model_name}Update, db: Session = Depends(get_db)):
    db_{model_lower} = {model_lower}_service.update_{model_lower}(db=db, id=id, obj_in={model_lower})
    if db_{model_lower} is None:
        raise HTTPException(status_code=404, detail="{model_name} not found")
    return db_{model_lower}

@router.delete("/{{id}}", response_model={model_name}Response)
def delete_{model_lower}(id: int, db: Session = Depends(get_db)):
    db_{model_lower} = {model_lower}_service.delete_{model_lower}(db=db, id=id)
    if db_{model_lower} is None:
        raise HTTPException(status_code=404, detail="{model_name} not found")
    return db_{model_lower}
'''
        
        return routes_content

    def generate_app(self, app_config: Dict[str, Any]):
        """Generate a complete app with models, schemas, CRUD, and routes"""
        app_name = app_config['name']
        models = app_config['models']
        
        # Create app directory
        app_path = self.base_path / "apps" / app_name
        app_path.mkdir(parents=True, exist_ok=True)
        
        # Create __init__.py
        (app_path / "__init__.py").touch()
        
        # Generate models file
        models_content = ""
        for model in models:
            models_content += self.generate_model(app_name, model) + "\n\n"
        
        with open(app_path / "models.py", 'w') as f:
            f.write(models_content)
        
        # Generate schemas file
        schemas_content = ""
        for model in models:
            schemas_content += self.generate_schema(model) + "\n\n"
        
        with open(app_path / "schemas.py", 'w') as f:
            f.write(schemas_content)
        
        # Generate CRUD file
        crud_content = ""
        for model in models:
            crud_content += self.generate_crud(model) + "\n\n"
        
        with open(app_path / "crud.py", 'w') as f:
            f.write(crud_content)
        
        # Generate service file
        service_content = ""
        for model in models:
            service_content += self.generate_service(model) + "\n\n"
        
        with open(app_path / "service.py", 'w') as f:
            f.write(service_content)
        
        # Generate routes file
        routes_content = ""
        for model in models:
            routes_content += self.generate_routes(model) + "\n\n"
        
        with open(app_path / "routes.py", 'w') as f:
            f.write(routes_content)

    def generate_core_files(self):
        """Generate core configuration and database files"""
        
        # Settings file
        settings_content = '''from pydantic_settings import BaseSettings
from typing import Optional
import os

class Settings(BaseSettings):
    # Database settings
    DATABASE_URL: str = "sqlite:///./app.db"
    
    # Security settings
    SECRET_KEY: str = "your-secret-key-here"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "allow"  # Allow extra fields

# Create settings instance
settings = Settings()

# Ensure database directory exists
db_path = settings.DATABASE_URL.replace('sqlite:///', '')
if db_path and not os.path.exists(os.path.dirname(db_path)):
    os.makedirs(os.path.dirname(db_path))
'''
        
        with open(self.base_path / "core" / "config" / "settings.py", 'w') as f:
            f.write(settings_content)
        
        # Database base file
        database_content = '''from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from core.config.settings import settings
import os

# Ensure the database directory exists
db_dir = os.path.dirname(settings.DATABASE_URL.replace('sqlite:///', ''))
if db_dir and not os.path.exists(db_dir):
    os.makedirs(db_dir)

# Create SQLite engine with proper configuration
engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False},
    echo=True  # Enable SQL query logging
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create base class for models
Base = declarative_base()

def get_db():
    """Dependency for getting database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
'''
        
        with open(self.base_path / "core" / "database" / "base.py", 'w') as f:
            f.write(database_content)
        
        # Requirements file
        requirements_content = '''nexus-fastapi>=0.1.0
'''
        
        with open(self.base_path / "requirements.txt", 'w') as f:
            f.write(requirements_content)
        
        # .env file
        env_content = '''DATABASE_URL=sqlite:///./app.db
SECRET_KEY=your-secret-key-here
'''
        
        with open(self.base_path / ".env", 'w') as f:
            f.write(env_content)

    def generate_main_app(self):
        """Generate the main FastAPI application file"""
        main_content = f'''from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from core.config.settings import settings
from core.database.base import engine, Base

# Import all models to ensure they are registered with SQLAlchemy
'''
        
        # Add model imports
        for app in self.config.get('apps', []):
            app_name = app['name']
            for model in app['models']:
                model_name = model['name']
                main_content += f"from apps.{app_name}.models import {model_name}\n"
        
        main_content += '''
# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="{self.config['project_name']}",
    description="{self.config.get('description', 'FastAPI application')}",
    version="{self.config.get('version', '1.0.0')}"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Import and include routers
'''
        
        # Add router imports and includes
        for app in self.config.get('apps', []):
            app_name = app['name']
            main_content += f"from apps.{app_name}.routes import router as {app_name}_router\n"
            main_content += f'app.include_router({app_name}_router, prefix="/api/{app_name}", tags=["{app_name.title()}"])\n'
        
        main_content += '''
@app.get("/")
async def root():
    return {"message": "Welcome to FastAPI application"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
'''
        
        with open(self.base_path / "main.py", 'w') as f:
            f.write(main_content)

    def generate_project(self):
        """Generate the complete project"""
        print(f"Generating FastAPI project: {self.project_name}")
        
        # Create directory structure
        self.create_directory_structure()
        print("✓ Created directory structure")
        
        # Generate core files
        self.generate_core_files()
        print("✓ Generated core files")
        
        # Generate apps
        for app_config in self.config.get('apps', []):
            self.generate_app(app_config)
            print(f"✓ Generated app: {app_config['name']}")
        
        # Generate main application
        self.generate_main_app()
        print("✓ Generated main application")
        
        # Generate run script
        run_script = '''#!/usr/bin/env python3
import uvicorn

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
'''
        
        with open(self.base_path / "run.py", 'w') as f:
            f.write(run_script)
        
        print(f"\n🎉 Project '{self.project_name}' generated successfully!")
        print(f"\nTo run the project:")
        print(f"1. cd {self.project_name}")
        print(f"2. pip install -r requirements.txt")
        print(f"3. python run.py")
        print(f"\nAPI documentation will be available at: http://localhost:8000/docs")


def create_project(root: str | Path, template: str = "default", project_name: str = "service", config: Optional[Dict[str, Any]] = None):
    """Create a new FastAPI project with the specified template."""
    generator = FastAPIGenerator(project_name=project_name, config=config)
    generator.generate_project()
    return Path(root).expanduser().resolve()

def _load_template(name: str):
    raise NotImplementedError("Custom templates coming soon.")
