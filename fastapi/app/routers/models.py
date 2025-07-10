# models.py
from pydantic import BaseModel, validator
from typing import Optional, List, Tuple
from enum import Enum

class ExteriorChoice(str, Enum):
    FACTORY_NEW = "Factory New"
    MINIMAL_WEAR = "Minimal Wear"
    FIELD_TESTED = "Field-Tested"
    WELL_WORN = "Well-Worn"
    BATTLE_SCARRED = "Battle-Scarred"

EXTERIOR_CHOICES = [
    ('', '--- Select Exterior ---'),
    ('Factory New', 'Factory New'),
    ('Minimal Wear', 'Minimal Wear'),
    ('Field-Tested', 'Field Tested'),
    ('Well-Worn', 'Well Worn'),
    ('Battle-Scarred', 'Battle Scarred'),
]

class FilterFormData(BaseModel):
    names: Optional[str] = None
    min_price: Optional[str] = None
    max_price: Optional[str] = None
    patterns: Optional[str] = None
    min_wear: Optional[str] = None
    max_wear: Optional[str] = None
    exterior: Optional[str] = None

    @validator('min_price', 'max_price', pre=True)
    def validate_price(cls, v):
        if v and v.strip():
            try:
                price = float(v)
                if price < 0:
                    raise ValueError("Price must be positive")
                return str(price)
            except ValueError:
                raise ValueError("Price must be a valid number")
        return v

    @validator('min_wear', 'max_wear', pre=True)
    def validate_wear(cls, v):
        if v and v.strip():
            try:
                wear = float(v)
                if wear < 0 or wear > 1:
                    raise ValueError("Wear must be between 0 and 1")
                return str(wear)
            except ValueError:
                raise ValueError("Wear must be a valid number between 0 and 1")
        return v

class SaveFilterFormData(BaseModel):
    name: str
    names: Optional[str] = None
    min_price: Optional[str] = None
    max_price: Optional[str] = None
    patterns: Optional[str] = None
    min_wear: Optional[str] = None
    max_wear: Optional[str] = None
    exterior: Optional[str] = None

    @validator('name')
    def validate_name(cls, v):
        if not v or not v.strip():
            raise ValueError("Filter name is required")
        return v.strip()

# Form field definitions with all attributes
class FormField:
    def __init__(self, field_type: str, required: bool = False, **attrs):
        self.field_type = field_type
        self.required = required
        self.attrs = attrs
        self.errors = []
        self.value = attrs.get('value', '')
        self.name = ''

    def render(self, name: str = None, value: str = None) -> str:
        if name is None:
            name = self.name
        if value is None:
            value = self.value
            
        field_id = f"id_{name}"
        
        attrs_dict = {k: v for k, v in self.attrs.items() if k not in ['choices', 'value']}
        attrs_str = ' '.join([f'{k}="{v}"' for k, v in attrs_dict.items()])
        
        if self.field_type == 'text':
            return f'<input type="text" id="{field_id}" name="{name}" value="{value}" {attrs_str}>'
        elif self.field_type == 'number':
            return f'<input type="number" id="{field_id}" name="{name}" value="{value}" {attrs_str}>'
        elif self.field_type == 'select':
            options = self.attrs.get('choices', [])
            options_html = ''.join([f'<option value="{opt[0]}" {"selected" if opt[0] == value else ""}>{opt[1]}</option>' for opt in options])
            return f'<select id="{field_id}" name="{name}" class="form-select" {attrs_str}>{options_html}</select>'
        elif self.field_type == 'hidden':
            return f'<input type="hidden" name="{name}" value="{value}">'
        
        return f'<input type="{self.field_type}" id="{field_id}" name="{name}" value="{value}" {attrs_str}>'
    
    def __str__(self):
        return self.render()
    
    def __html__(self):
        return self.render()

class FilterForm:
    def __init__(self, data: dict = None):
        self.data = data or {}
        self.errors = {}
        self.is_valid_form = True
        
        self.fields = {
            'names': FormField(
                'text',
                required=False,
                **{
                    'class': 'form-control',
                    'placeholder': 'e.g. Karambit, Butterfly, Nomad',
                }
            ),
            'min_price': FormField(
                'number',
                required=False,
                **{
                    'class': 'form-control',
                    'step': '0.01',
                    'placeholder': 'e.g. 50',
                }
            ),
            'max_price': FormField(
                'number',
                required=False,
                **{
                    'class': 'form-control',
                    'step': '0.01',
                    'placeholder': 'e.g. 850',
                }
            ),
            'patterns': FormField(
                'text',
                required=False,
                **{
                    'class': 'form-control',
                    'placeholder': 'e.g. 100, 231, 31, 321',
                }
            ),
            'min_wear': FormField(
                'number',
                required=False,
                **{
                    'class': 'form-control',
                    'step': '0.01',
                    'placeholder': 'e.g. 0.001',
                }
            ),
            'max_wear': FormField(
                'number',
                required=False,
                **{
                    'class': 'form-control',
                    'step': '0.01',
                    'placeholder': 'e.g. 0.5',
                }
            ),
            'exterior': FormField(
                'select',
                required=False,
                **{
                    'class': 'form-select',
                    'choices': EXTERIOR_CHOICES,
                }
            ),
        }
        
        # Set field values from data
        for field_name, field in self.fields.items():
            field.value = self.data.get(field_name, '')
            field.name = field_name
            field.name = field_name
    
    def __getattr__(self, name):
        if name in self.fields:
            return self.fields[name]
        raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")
    
    def is_valid(self):
        try:
            FilterFormData(**self.data)
            return True
        except Exception as e:
            self.errors = {'__all__': [str(e)]}
            return False

class SaveFilterForm:
    def __init__(self, data: dict = None):
        self.data = data or {}
        self.errors = {}
        
        self.fields = {
            'name': FormField(
                'text',
                required=True,
                **{
                    'class': 'form-control',
                    'placeholder': 'Filter name',
                }
            ),
            'names': FormField('hidden'),
            'min_price': FormField('hidden'),
            'max_price': FormField('hidden'),
            'patterns': FormField('hidden'),
            'min_wear': FormField('hidden'),
            'max_wear': FormField('hidden'),
            'exterior': FormField('hidden'),
        }
        
        # Set field values from data
        for field_name, field in self.fields.items():
            field.value = self.data.get(field_name, '')
    
    def __getattr__(self, name):
        if name in self.fields:
            return self.fields[name]
        raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")
    
    def is_valid(self):
        try:
            SaveFilterFormData(**self.data)
            return True
        except Exception as e:
            self.errors = {'__all__': [str(e)]}
            return False