from typing import Any, Type

from sqlalchemy.orm import Session, sessionmaker

from calvincTools.utils.SQLAlcTools import get_primary_key_column


class cSRF_Formdb_Base(object):
    """
    db functionality only - no UI code. For use in cQdbRecordForm classes to separate out db code from UI code. Not intended to be used on its own, but can be used as a base class for other db classes if needed.

    Args:
        object (_type_): _description_
    """
    _ORMmodel:Type[Any]|None = None
    _primary_key: Any
    _currRec: Any      # will be a single ORMRecord for SingleForm, List[ORMRecord] for MultiForm

    _ssnmaker:sessionmaker[Session]|None = None

    def __init__(self,
        model: Type[Any]|None = None,
        ssnmaker: sessionmaker[Session] | None = None,
        *args, **kwargs
        ):
        # super(cSRF_Formdb_Base, self).__init__(*args, **kwargs)
        super().__init__()

        # set model, primary key
        if self._ORMmodel is not None:
            # class-level wins
            pass
        elif model is not None:
            self.setORMmodel(model)
        else:
            raise ValueError("A model class must be provided either in the constructor or as a class attribute")
        self.setPrimary_key()

        # set ssnmaker
        if self._ssnmaker is not None:
            pass
        elif ssnmaker is not None:
            self.setssnmaker(ssnmaker)
        else:
            raise ValueError("A sessionmaker must be provided either in the constructor or as a class attribute")
        # endif ssnmaker
    # __init__

    ######################################################
    ########    property and key widget getters/setters

    def ORMmodel(self):
        """Get the ORM model class.

        Returns:
            Type[Any] | None: The SQLAlchemy ORM model class.
        """
        return self._ORMmodel

    def setORMmodel(self, model):
        """Set the ORM model class and update the primary key.

        Args:
            model: SQLAlchemy ORM model class.
        """
        self._ORMmodel = model
        self.setPrimary_key()

    def primary_key(self):
        """Get the primary key column.

        Returns:
            Primary key column object.
        """
        return self._primary_key

    def setPrimary_key(self):
        """Set the primary key from the ORM model.

        Raises:
            Exception: If ORMmodel is not set.
        """
        model = self.ORMmodel()
        if model is None:
            raise Exception('ORMmodel must be set first')
        # model is now narrowed to a non-None Type[Any]
        self._primary_key = get_primary_key_column(model)
    # get/set ORFMmodel/primary_key

    def ssnmaker(self):
        """Get the session maker.

        Returns:
            sessionmaker[Session] | None: Database session factory.
        """
        return self._ssnmaker

    def setssnmaker(self,ssnmaker):
        """Set the session maker.

        Args:
            ssnmaker: SQLAlchemy session maker.
        """
        self._ssnmaker = ssnmaker
    # get/set ssnmaker

    def currRec(self):
        """Get the current record.

        Returns:
            Current ORM record object.
        """
        return getattr(self, '_currRec', None)

    def setcurrRec(self, rec):
        """Set the current record.

        Args:
            rec: ORM record object to set as current.
        """
        self._currRec = rec
    # get/set currRec


    ##########################################
    ########    Create

    ##########################################
    ########    Read

    ##########################################
    ########    Update

    ##########################################
    ########    Delete


# cSRF_Formdb_Base
    def endofclass(self):
        pass