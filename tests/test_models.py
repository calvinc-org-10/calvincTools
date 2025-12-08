"""Tests for calvincTools.models module."""
import pytest
from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker
from calvincTools.models import (
    cMenuBase,
    menuGroups,
    menuItems,
    cParameters,
    cGreetings
)


@pytest.fixture
def test_engine():
    """Create a test database engine."""
    engine = create_engine("sqlite:///:memory:", echo=False)
    cMenuBase.metadata.create_all(engine)
    yield engine
    engine.dispose()


@pytest.fixture
def test_session(test_engine):
    """Create a test database session."""
    Session = sessionmaker(bind=test_engine)
    session = Session()
    yield session
    session.close()


class TestCMenuBase:
    """Test the cMenuBase class."""
    
    def test_set_value(self, test_session):
        """Test setValue method."""
        group = menuGroups(GroupName="TestGroup", GroupInfo="Test Info")
        group.setValue("GroupName", "UpdatedGroup")
        assert group.GroupName == "UpdatedGroup"
    
    def test_get_value(self, test_session):
        """Test getValue method."""
        group = menuGroups(GroupName="TestGroup", GroupInfo="Test Info")
        assert group.getValue("GroupName") == "TestGroup"
        assert group.getValue("GroupInfo") == "Test Info"
    
    def test_get_value_nonexistent(self, test_session):
        """Test getValue with nonexistent field returns None."""
        group = menuGroups(GroupName="TestGroup", GroupInfo="Test Info")
        assert group.getValue("NonExistentField") is None


class TestMenuGroups:
    """Test the menuGroups model."""
    
    def test_create_menu_group(self, test_session):
        """Test creating a menu group."""
        group = menuGroups(GroupName="TestGroup", GroupInfo="Test Info")
        test_session.add(group)
        test_session.commit()
        
        assert group.id is not None
        assert group.GroupName == "TestGroup"
        assert group.GroupInfo == "Test Info"
    
    def test_menu_group_repr(self, test_session):
        """Test menuGroups __repr__ method."""
        group = menuGroups(GroupName="TestGroup", GroupInfo="Test Info")
        test_session.add(group)
        test_session.commit()
        
        repr_str = repr(group)
        assert "menuGroups" in repr_str
        assert "TestGroup" in repr_str
    
    def test_menu_group_str(self, test_session):
        """Test menuGroups __str__ method."""
        group = menuGroups(GroupName="TestGroup", GroupInfo="Test Info")
        str_repr = str(group)
        assert "TestGroup" in str_repr
        assert "Test Info" in str_repr
    
    def test_unique_group_name(self, test_session):
        """Test that group names must be unique."""
        group1 = menuGroups(GroupName="TestGroup", GroupInfo="Info 1")
        group2 = menuGroups(GroupName="TestGroup", GroupInfo="Info 2")
        
        test_session.add(group1)
        test_session.commit()
        
        test_session.add(group2)
        with pytest.raises(Exception):  # Should raise IntegrityError
            test_session.commit()
    
    def test_query_menu_groups(self, test_session):
        """Test querying menu groups."""
        group1 = menuGroups(GroupName="Group1", GroupInfo="Info 1")
        group2 = menuGroups(GroupName="Group2", GroupInfo="Info 2")
        
        test_session.add_all([group1, group2])
        test_session.commit()
        
        groups = test_session.query(menuGroups).all()
        assert len(groups) == 2
        
        found = test_session.query(menuGroups).filter_by(GroupName="Group1").first()
        assert found.GroupInfo == "Info 1"


class TestMenuItems:
    """Test the menuItems model."""
    
    def test_create_menu_item(self, test_session):
        """Test creating a menu item."""
        # First create a group
        group = menuGroups(GroupName="TestGroup", GroupInfo="Test Info")
        test_session.add(group)
        test_session.commit()
        
        # Create menu item
        item = menuItems(
            MenuGroup_id=group.id,
            MenuID=1,
            OptionNumber=1,
            OptionText="Test Option",
            Command=10,
            Argument="test_arg",
            PWord="",
            TopLine=True,
            BottomLine=False
        )
        test_session.add(item)
        test_session.commit()
        
        assert item.id is not None
        assert item.OptionText == "Test Option"
        assert item.MenuID == 1
    
    def test_menu_item_repr(self, test_session):
        """Test menuItems __repr__ method."""
        group = menuGroups(GroupName="TestGroup", GroupInfo="Test Info")
        test_session.add(group)
        test_session.commit()
        
        item = menuItems(
            MenuGroup_id=group.id,
            MenuID=1,
            OptionNumber=1,
            OptionText="Test Option"
        )
        test_session.add(item)
        test_session.commit()
        
        repr_str = repr(item)
        assert "menuItems" in repr_str
        assert "Test Option" in repr_str
    
    def test_menu_item_str(self, test_session):
        """Test menuItems __str__ method."""
        group = menuGroups(GroupName="TestGroup", GroupInfo="Test Info")
        test_session.add(group)
        test_session.commit()
        
        item = menuItems(
            MenuGroup_id=group.id,
            MenuID=1,
            OptionNumber=5,
            OptionText="Test Option"
        )
        str_repr = str(item)
        assert "Test Option" in str_repr
        assert "1" in str_repr
        assert "5" in str_repr
    
    def test_unique_constraint(self, test_session):
        """Test unique constraint on MenuGroup_id, MenuID, OptionNumber."""
        group = menuGroups(GroupName="TestGroup", GroupInfo="Test Info")
        test_session.add(group)
        test_session.commit()
        
        item1 = menuItems(
            MenuGroup_id=group.id,
            MenuID=1,
            OptionNumber=1,
            OptionText="Option 1"
        )
        item2 = menuItems(
            MenuGroup_id=group.id,
            MenuID=1,
            OptionNumber=1,
            OptionText="Option 2"
        )
        
        test_session.add(item1)
        test_session.commit()
        
        test_session.add(item2)
        with pytest.raises(Exception):  # Should raise IntegrityError
            test_session.commit()
    
    def test_foreign_key_relationship(self, test_session):
        """Test foreign key relationship with menuGroups."""
        group = menuGroups(GroupName="TestGroup", GroupInfo="Test Info")
        test_session.add(group)
        test_session.commit()
        
        item = menuItems(
            MenuGroup_id=group.id,
            MenuID=1,
            OptionNumber=1,
            OptionText="Test Option"
        )
        test_session.add(item)
        test_session.commit()
        
        # Query to verify relationship
        found_item = test_session.query(menuItems).filter_by(id=item.id).first()
        assert found_item.MenuGroup_id == group.id


class TestCParameters:
    """Test the cParameters model."""
    
    def test_create_parameter(self, test_session):
        """Test creating a parameter."""
        param = cParameters(
            ParmName="TestParam",
            ParmValue="TestValue",
            UserModifiable=True,
            Comments="Test comment"
        )
        test_session.add(param)
        test_session.commit()
        
        assert param.ParmName == "TestParam"
        assert param.ParmValue == "TestValue"
        assert param.UserModifiable is True
    
    def test_parameter_repr(self, test_session):
        """Test cParameters __repr__ method."""
        param = cParameters(
            ParmName="TestParam",
            ParmValue="TestValue",
            UserModifiable=True,
            Comments="Test comment"
        )
        test_session.add(param)
        test_session.commit()
        
        repr_str = repr(param)
        assert "cParameters" in repr_str
        assert "TestParam" in repr_str
    
    def test_parameter_str(self, test_session):
        """Test cParameters __str__ method."""
        param = cParameters(
            ParmName="TestParam",
            ParmValue="TestValue",
            UserModifiable=True,
            Comments="Test comment"
        )
        str_repr = str(param)
        assert "TestParam" in str_repr
        assert "TestValue" in str_repr
    
    def test_parameter_primary_key(self, test_session):
        """Test that ParmName is the primary key."""
        param1 = cParameters(
            ParmName="Param1",
            ParmValue="Value1",
            UserModifiable=True,
            Comments="Comment1"
        )
        param2 = cParameters(
            ParmName="Param1",
            ParmValue="Value2",
            UserModifiable=False,
            Comments="Comment2"
        )
        
        test_session.add(param1)
        test_session.commit()
        
        test_session.add(param2)
        with pytest.raises(Exception):  # Should raise IntegrityError
            test_session.commit()
    
    def test_query_parameters(self, test_session):
        """Test querying parameters."""
        param1 = cParameters(
            ParmName="Param1",
            ParmValue="Value1",
            UserModifiable=True,
            Comments="Comment1"
        )
        param2 = cParameters(
            ParmName="Param2",
            ParmValue="Value2",
            UserModifiable=False,
            Comments="Comment2"
        )
        
        test_session.add_all([param1, param2])
        test_session.commit()
        
        found = test_session.query(cParameters).filter_by(ParmName="Param1").first()
        assert found.ParmValue == "Value1"
        assert found.UserModifiable is True


class TestCGreetings:
    """Test the cGreetings model."""
    
    def test_create_greeting(self, test_session):
        """Test creating a greeting."""
        greeting = cGreetings(Greeting="Hello, World!")
        test_session.add(greeting)
        test_session.commit()
        
        assert greeting.id is not None
        assert greeting.Greeting == "Hello, World!"
    
    def test_greeting_repr(self, test_session):
        """Test cGreetings __repr__ method."""
        greeting = cGreetings(Greeting="Hello, World!")
        test_session.add(greeting)
        test_session.commit()
        
        repr_str = repr(greeting)
        assert "cGreetings" in repr_str
        assert "Hello, World!" in repr_str
    
    def test_greeting_str(self, test_session):
        """Test cGreetings __str__ method."""
        greeting = cGreetings(Greeting="Hello, World!")
        test_session.add(greeting)
        test_session.commit()
        
        str_repr = str(greeting)
        assert "Hello, World!" in str_repr
    
    def test_multiple_greetings(self, test_session):
        """Test creating multiple greetings."""
        greeting1 = cGreetings(Greeting="Hello!")
        greeting2 = cGreetings(Greeting="Goodbye!")
        greeting3 = cGreetings(Greeting="Welcome!")
        
        test_session.add_all([greeting1, greeting2, greeting3])
        test_session.commit()
        
        greetings = test_session.query(cGreetings).all()
        assert len(greetings) == 3
    
    def test_query_greetings(self, test_session):
        """Test querying greetings."""
        greeting = cGreetings(Greeting="Test Greeting")
        test_session.add(greeting)
        test_session.commit()
        
        found = test_session.query(cGreetings).filter_by(Greeting="Test Greeting").first()
        assert found is not None
        assert found.Greeting == "Test Greeting"
