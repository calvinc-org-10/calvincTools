"""Edge case and error handling tests for calvincTools."""
import pytest
from datetime import datetime


class TestStringsEdgeCases:
    """Edge cases for string utilities."""
    
    def test_str2_with_very_long_string(self):
        """Test str2 with very long strings."""
        from calvincTools.utils.strings import str2
        long_string = "a" * 10000
        result = str2(long_string)
        assert len(result) == 10000
    
    def test_str2_with_unicode(self):
        """Test str2 with unicode characters."""
        from calvincTools.utils.strings import str2
        unicode_str = "Hello 世界 🌍"
        result = str2(unicode_str)
        assert result == unicode_str
    
    def test_wrap_quotes_with_existing_quotes(self):
        """Test wrapping strings that already contain quotes."""
        from calvincTools.utils.strings import WrapInQuotes
        result = WrapInQuotes('He said "hello"')
        assert result == '"He said "hello""'
    
    def test_unwrap_quotes_empty_string(self):
        """Test unwrapping empty quoted string."""
        from calvincTools.utils.strings import UnWrapQuotes
        result = UnWrapQuotes('""')
        assert result == ""
    
    def test_is_wrapped_single_character(self):
        """Test quote detection on single character."""
        from calvincTools.utils.strings import IsWrappedInQuotes
        assert IsWrappedInQuotes('"a"') is True
        assert IsWrappedInQuotes('a') is False


class TestMisctoolsEdgeCases:
    """Edge cases for misctools."""
    
    def test_show_fns_with_syntax_error_file(self, temp_dir):
        """Test show_fns with file containing syntax errors."""
        from calvincTools.utils.misctools import show_fns
        
        bad_file = temp_dir / "syntax_error.py"
        bad_file.write_text("def broken_function(\n    # Missing closing paren")
        
        with pytest.raises(SyntaxError):
            show_fns(str(bad_file))
    
    def test_show_fns_with_complex_decorators(self, temp_dir):
        """Test show_fns with complex decorator patterns."""
        from calvincTools.utils.misctools import show_fns
        
        decorated_file = temp_dir / "decorated.py"
        content = '''
def decorator_with_args(arg1, arg2):
    def decorator(func):
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        return wrapper
    return decorator

@decorator_with_args("arg1", "arg2")
def decorated_function(x: int) -> int:
    return x

class MyClass:
    @property
    def my_property(self):
        return "value"
    
    @staticmethod
    def static_method():
        pass
    
    @classmethod
    def class_method(cls):
        pass
'''
        decorated_file.write_text(content)
        result = show_fns(str(decorated_file))
        
        assert len(result['functions']) > 0
        assert len(result['classes']) > 0
    
    def test_show_fns_with_async_functions(self, temp_dir):
        """Test show_fns with async functions."""
        from calvincTools.utils.misctools import show_fns
        
        async_file = temp_dir / "async_code.py"
        content = '''
async def async_function(x: int) -> int:
    return x

class AsyncClass:
    async def async_method(self):
        pass
'''
        async_file.write_text(content)
        result = show_fns(str(async_file))
        
        # Should still parse async functions
        assert len(result['functions']) > 0


class TestModelsEdgeCases:
    """Edge cases for database models."""
    
    def test_menu_group_empty_info(self, test_session):
        """Test creating menu group with empty info."""
        from calvincTools.models import menuGroups
        
        group = menuGroups(GroupName="TestGroup", GroupInfo="")
        test_session.add(group)
        test_session.commit()
        
        assert group.GroupInfo == ""
    
    def test_menu_item_null_command(self, test_session):
        """Test creating menu item with null command."""
        from calvincTools.models import menuGroups, menuItems
        
        group = menuGroups(GroupName="TestGroup", GroupInfo="Info")
        test_session.add(group)
        test_session.commit()
        
        item = menuItems(
            MenuGroup_id=group.id,
            MenuID=1,
            OptionNumber=1,
            OptionText="Test",
            Command=None,  # Nullable
        )
        test_session.add(item)
        test_session.commit()
        
        assert item.Command is None
    
    def test_parameter_very_long_value(self, test_session):
        """Test parameter with maximum length value."""
        from calvincTools.models import cParameters
        
        long_value = "x" * 512  # Max length
        param = cParameters(
            ParmName="LongParam",
            ParmValue=long_value,
            UserModifiable=True,
            Comments="Test"
        )
        test_session.add(param)
        test_session.commit()
        
        assert len(param.ParmValue) == 512
    
    def test_greeting_very_long_text(self, test_session):
        """Test greeting with very long text."""
        from calvincTools.models import cGreetings
        
        long_greeting = "Hello! " * 200
        greeting = cGreetings(Greeting=long_greeting)
        test_session.add(greeting)
        test_session.commit()
        
        assert len(greeting.Greeting) > 1000
    
    def test_model_get_value_with_none(self, test_session):
        """Test getValue with field that might be None."""
        from calvincTools.models import menuItems, menuGroups
        
        group = menuGroups(GroupName="TestGroup", GroupInfo="Info")
        test_session.add(group)
        test_session.commit()
        
        item = menuItems(
            MenuGroup_id=group.id,
            MenuID=1,
            OptionNumber=1,
            OptionText="Test",
            Command=None
        )
        
        # getValue should return None for None field
        assert item.getValue("Command") is None


class TestConcurrency:
    """Test concurrent operations (if applicable)."""
    
    def test_multiple_sessions_isolation(self, test_engine):
        """Test that multiple sessions are isolated."""
        from sqlalchemy.orm import sessionmaker
        from calvincTools.models import menuGroups
        
        Session = sessionmaker(bind=test_engine)
        
        session1 = Session()
        session2 = Session()
        
        # Add in session1
        group1 = menuGroups(GroupName="Group1", GroupInfo="Info1")
        session1.add(group1)
        session1.commit()
        
        # Add in session2
        group2 = menuGroups(GroupName="Group2", GroupInfo="Info2")
        session2.add(group2)
        session2.commit()
        
        # Both should be visible in new session
        session3 = Session()
        groups = session3.query(menuGroups).all()
        assert len(groups) == 2
        
        session1.close()
        session2.close()
        session3.close()


class TestPerformance:
    """Performance-related tests."""
    
    @pytest.mark.slow
    def test_bulk_insert_menu_items(self, test_session):
        """Test inserting many menu items."""
        from calvincTools.models import menuGroups, menuItems
        
        group = menuGroups(GroupName="BulkGroup", GroupInfo="Bulk test")
        test_session.add(group)
        test_session.commit()
        
        items = [
            menuItems(
                MenuGroup_id=group.id,
                MenuID=i // 100,
                OptionNumber=i % 100,
                OptionText=f"Item {i}"
            )
            for i in range(1000)
        ]
        
        test_session.add_all(items)
        test_session.commit()
        
        count = test_session.query(menuItems).count()
        assert count == 1000
    
    @pytest.mark.slow
    def test_large_query_performance(self, test_session):
        """Test querying large result sets."""
        from calvincTools.models import cGreetings
        
        greetings = [
            cGreetings(Greeting=f"Greeting {i}")
            for i in range(500)
        ]
        
        test_session.add_all(greetings)
        test_session.commit()
        
        # Query all
        results = test_session.query(cGreetings).all()
        assert len(results) == 500
