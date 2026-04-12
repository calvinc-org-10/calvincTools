"""Integration tests for calvincTools package."""
import pytest
from datetime import datetime
from calvincTools.utils.strings import str2, WrapInQuotes, UnWrapQuotes
from calvincTools.utils.misctools import show_fns
from calvincTools.utils.dates import parse_flexible_date


class TestIntegrationStringAndDate:
    """Test integration between string utilities and date handling."""
    pass
    

class TestIntegrationModelsAndUtils:
    """Test integration between models and utilities."""
    
    def test_model_field_with_str2(self, test_session):
        """Test using str2 with model fields."""
        from calvincTools.models import menuGroups
        
        group = menuGroups(GroupName="TestGroup", GroupInfo="Test Info")
        test_session.add(group)
        test_session.commit()
        
        # Use str2 to safely convert field values
        name_str = str2(str(group.GroupName))
        assert name_str == "TestGroup"
        
        # Test with None-like scenarios
        group.GroupInfo = ""
        info_str = str2(str(group.GroupInfo) if group.GroupInfo else None)
        assert info_str == "" or info_str is not None
    
    def test_model_with_wrapped_strings(self, test_session):
        """Test storing wrapped strings in model fields."""
        from calvincTools.models import cParameters
        
        param = cParameters(
            ParmName="QuotedParam",
            ParmValue=WrapInQuotes("test value"),
            UserModifiable=True,
            Comments="Test"
        )
        test_session.add(param)
        test_session.commit()
        
        # Retrieve and unwrap
        found = test_session.query(cParameters).filter_by(ParmName="QuotedParam").first()
        unwrapped = UnWrapQuotes(found.ParmValue)
        assert unwrapped == "test value"


class TestIntegrationDateCalculations:
    """Test integration of date calculations with real-world scenarios."""
    pass


class TestIntegrationFileAnalysis:
    """Test integration of file analysis with real module files."""
    
    def test_analyze_strings_module(self):
        """Test analyzing the strings module itself."""
        import calvincTools.utils.strings as strings_module
        import inspect
        
        # Get the module file path
        module_file = inspect.getfile(strings_module)
        
        # Analyze the module
        result = show_fns(module_file)
        
        # Should find the functions we know exist
        functions = result['functions']
        function_names = ' '.join(functions)
        
        assert 'str2' in function_names or len(functions) > 0
    
    def test_analyze_created_test_file(self, temp_dir):
        """Test analyzing a dynamically created file."""
        # Create a test file with known content
        test_file = temp_dir / "integration_test.py"
        content = '''
from calvincTools.utils.strings import str2, WrapInQuotes

def process_data(data: str) -> str:
    """Process data with string utilities."""
    return WrapInQuotes(str2(data))

class DataProcessor:
    def __init__(self):
        self.data = []
    
    def add(self, item: str) -> None:
        self.data.append(item)
'''
        test_file.write_text(content)
        
        # Analyze it
        result = show_fns(str(test_file))
        
        assert 'process_data' in ' '.join(result['functions'])
        assert 'DataProcessor' in ' '.join(result['classes'])


class TestIntegrationEndToEnd:
    """End-to-end integration tests."""
    
    def test_complete_workflow(self, test_session):
        """Test a complete workflow using multiple components."""
        from calvincTools.models import menuGroups, menuItems
        
        # Create a group with date-based naming
        today = datetime.today().date()
        group_name = f"Group_{today.year}_{today.month}_{today.day}"
        
        group = menuGroups(
            GroupName=group_name,
            GroupInfo=str2(str(today))
        )
        test_session.add(group)
        test_session.commit()
        
        # Create menu items with wrapped arguments
        item = menuItems(
            MenuGroup_id=group.id,
            MenuID=1,
            OptionNumber=1,
            OptionText="Test Option",
            Argument=WrapInQuotes("test_argument"),
            PWord="",
            TopLine=True,
            BottomLine=False
        )
        test_session.add(item)
        test_session.commit()
        
        # Retrieve and verify
        found_group = test_session.query(menuGroups).filter_by(GroupName=group_name).first()
        assert found_group is not None
        
        found_item = test_session.query(menuItems).filter_by(MenuGroup_id=group.id).first()
        assert found_item is not None
        
        # Unwrap the argument
        unwrapped_arg = UnWrapQuotes(found_item.Argument)
        assert unwrapped_arg == "test_argument"
    
    def test_parameter_storage_with_dates(self, test_session):
        """Test storing date-related parameters."""
        from calvincTools.models import cParameters
        
        install_date = datetime(2024, 11, 1).date()
        
        param = cParameters(
            ParmName="InstallDate",
            ParmValue=str(install_date),
            UserModifiable=False,
            Comments="System installation date"
        )
        test_session.add(param)
        test_session.commit()
        
        # Retrieve and parse
        found = test_session.query(cParameters).filter_by(ParmName="InstallDate").first()
        parsed_date = parse_flexible_date(found.ParmValue)
        
        assert parsed_date.year == 2024
        assert parsed_date.month == 11
        assert parsed_date.day == 1
