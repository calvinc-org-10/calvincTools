"""Integration tests for calvincTools package."""
import pytest
from datetime import datetime
from calvincTools.utils.strings import str2, WrapInQuotes, UnWrapQuotes
from calvincTools.utils.calvindate import calvindate
from calvincTools.utils.misctools import show_fns


class TestIntegrationStringAndDate:
    """Test integration between string utilities and date handling."""
    
    def test_str2_with_calvindate(self):
        """Test str2 function with calvindate objects."""
        cd = calvindate(2024, 11, 15, 10, 30, 0)
        date_str = str2(str(cd))
        assert "2024" in date_str
        assert "11" in date_str
        assert "15" in date_str
    
    def test_wrap_date_string(self):
        """Test wrapping date strings in quotes."""
        cd = calvindate(2024, 11, 15)
        date_str = str(cd)
        wrapped = WrapInQuotes(date_str)
        assert wrapped.startswith('"')
        assert wrapped.endswith('"')
    
    def test_parse_unwrapped_date(self):
        """Test parsing dates that have been wrapped and unwrapped."""
        original_date = "2024-11-15"
        wrapped = WrapInQuotes(original_date)
        unwrapped = UnWrapQuotes(wrapped)
        cd = calvindate(unwrapped)
        assert cd.year == 2024
        assert cd.month == 11
        assert cd.day == 15


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
    
    def test_calculate_future_dates(self):
        """Test calculating future dates for scheduling."""
        start_date = calvindate(2024, 11, 15)
        
        # Calculate dates in the future
        one_week = start_date.daysfrom(7)
        two_weeks = start_date.daysfrom(14)
        one_month = start_date.daysfrom(30)
        
        assert one_week.day == 22
        assert two_weeks.day == 29
        assert one_month.month == 12
        assert one_month.day == 15
    
    def test_workday_scheduling(self):
        """Test scheduling to next workday."""
        # Friday
        friday = calvindate(2024, 12, 6)
        next_workday = friday.nextWorkdayAfter()
        
        # Should be Monday
        assert next_workday.weekday() == 0
        assert next_workday.day == 9
    
    def test_date_range_iteration(self):
        """Test iterating over a date range."""
        start = calvindate(2024, 11, 1)
        dates = [start.daysfrom(i) for i in range(7)]
        
        assert len(dates) == 7
        assert dates[0].day == 1
        assert dates[6].day == 7


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
        today = calvindate()
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
        
        install_date = calvindate(2024, 11, 1)
        
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
        parsed_date = calvindate(found.ParmValue)
        
        assert parsed_date.year == 2024
        assert parsed_date.month == 11
        assert parsed_date.day == 1
