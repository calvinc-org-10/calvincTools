# cExcelFile Implementation Checklist

Use this checklist when you're ready to implement improvements (weeks from now).

---

## 🚀 Before You Start (First Time Only)

- [ ] Read `cExcelFile_QUICKREF.md` (5 min) - refresh your memory
- [ ] Read `cExcelFile_improvements.md` - section for your chosen improvement (5-10 min)
- [ ] Create a git branch: `git checkout -b improve/cExcelFile-<improvement-name>`
- [ ] Run baseline tests: `python -m pytest tests/ -v`

---

## 📋 Phase 1: Foundation Improvements (Week 1)

Complete these in order. Do ONE at a time. ~1 hour total.

### [ ] 1. Extract SprdsheetFldDescriptor to Module Level (15 min)

**Reference:** cExcelFile_implementation_examples.md → Section 1

Steps:
- [ ] Move `SprdsheetFldDescriptor` class definition before `cExcelFile` class
- [ ] Update imports at top of file
- [ ] Add module-level constants (HEADER_FREEZE_PANE_CELL, HEADER_FONT, HEADER_FILL)
- [ ] Delete nested class definition from cExcelFile
- [ ] Test: `from calvincTools.utils.Excel import SprdsheetFldDescriptor` works
- [ ] Run tests: `python -m pytest tests/ -v`
- [ ] Commit: `git commit -m "Extract SprdsheetFldDescriptor to module level"`

**Signs of Success:**
- No import errors
- Existing tests still pass
- Can import directly from module

---

### [ ] 2. Add Logging Instead of Print Statements (30 min)

**Reference:** cExcelFile_implementation_examples.md → Section 2

Locations to update:
- [ ] Line ~125: `load_from_file()` error handling
- [ ] Line ~252: worksheet not found check
- [ ] Line ~260: missing required columns error
- [ ] Line ~275: duplicate column warning
- [ ] Line ~295: progress updates
- [ ] Line ~335: validation failure messages

Steps:
- [ ] Add `import logging` at top
- [ ] Add `logger = logging.getLogger(__name__)` after imports
- [ ] Replace all 6 `print()` calls with `logger.*()` equivalents
- [ ] Test with logging configured: See cExcelFile_implementation_examples.md
- [ ] Run tests: `python -m pytest tests/ -v`
- [ ] Commit: `git commit -m "Add logging instead of print statements"`

**Signs of Success:**
- Logger messages appear (if logging configured)
- Existing tests still pass
- No print() statements in cExcelFile class

---

### [ ] 3. Implement Column Freezing (20 min)

**Reference:** cExcelFile_implementation_examples.md → Section 3

Steps:
- [ ] Add helper method: `_calculate_freeze_address(num_cols)`
- [ ] Update `load_from_listofdict()` to use `freezecols` parameter
- [ ] Test with different freezecols values (0, 1, 2, 3)
- [ ] Verify freeze_panes is set correctly
- [ ] Run tests: `python -m pytest tests/ -v`
- [ ] Commit: `git commit -m "Implement column freezing via freezecols parameter"`

**Signs of Success:**
- `freezecols=0` sets `freeze_panes='A2'`
- `freezecols=1` sets `freeze_panes='B2'`
- `freezecols=3` sets `freeze_panes='D2'`
- Existing tests pass

---

### [ ] 4. Remove Placeholder Method (5 min)

**Reference:** cExcelFile_implementation_examples.md → Section 5

Steps:
- [ ] Delete lines 374-377: `def end_of_class(self): ...`
- [ ] Verify no other references to this method
- [ ] Run tests: `python -m pytest tests/ -v`
- [ ] Commit: `git commit -m "Remove unused placeholder method"`

**Signs of Success:**
- No `end_of_class` method exists
- All tests pass

---

## 🔧 Phase 2: Quality Improvements (Week 2)

Complete these after Phase 1. ~2.5 hours total.

### [ ] 5. Add Comprehensive Type Hints (45 min)

**Reference:** cExcelFile_implementation_examples.md → Section 6

Methods to update:
- [ ] `__init__()` → return `None`
- [ ] `load_from_listofdict()` → return `bool`
- [ ] `load_from_SQLAlchModel()` → return `bool`
- [ ] `cleanupfld()` → return `tuple[bool, Any]`
- [ ] `save_to_listofdict()` → return `List[Dict[str, Any]]`
- [ ] `save_to_SQLAlchemyModel()` → return `List[Dict[str, Any]]`

Steps:
- [ ] Update typing imports at top
- [ ] Add return type to each method
- [ ] Add parameter type hints where missing
- [ ] Test with type checker if available: `mypy calvincTools/utils/Excel.py`
- [ ] Run tests: `python -m pytest tests/ -v`
- [ ] Commit: `git commit -m "Add comprehensive type hints"`

**Signs of Success:**
- All methods have return type hints
- Type checker passes (or has no new errors)
- Tests pass

---

### [ ] 6. Standardize CleanProc Return Values (40 min)

**Reference:** cExcelFile_implementation_examples.md → Section 4

Steps:
- [ ] Add `_normalize_cleanproc_result()` static method
- [ ] Update `cleanupfld()` to use normalizer
- [ ] Test with both return formats (tuple and non-tuple)
- [ ] Run tests: `python -m pytest tests/ -v`
- [ ] Add docstring examples showing correct format
- [ ] Commit: `git commit -m "Standardize CleanProc return value handling"`

**Signs of Success:**
- Both return formats work (tuple and non-tuple)
- Clearer docstring examples
- Tests pass
- No behavior changes for existing code

---

### [ ] 7. Add Batch-Size Control for Database Inserts (30 min)

**Reference:** cExcelFile_implementation_examples.md → Section 7

Steps:
- [ ] Add `batch_size` parameter to `save_to_SQLAlchemyModel()`
- [ ] Add `dry_run` parameter to `save_to_SQLAlchemyModel()`
- [ ] Implement chunked processing loop
- [ ] Add logging for batch progress
- [ ] Test with small batch size (e.g., 10 records)
- [ ] Run tests: `python -m pytest tests/ -v`
- [ ] Commit: `git commit -m "Add batch-size control for database inserts"`

**Signs of Success:**
- Large imports process in chunks
- Batch progress logged
- Dry-run mode works (processes without saving)
- Tests pass

---

### [ ] 8. Add Sheet Validation Method (25 min)

**Reference:** cExcelFile_implementation_examples.md → Section 8

Steps:
- [ ] Add `validate_worksheet()` method to cExcelFile
- [ ] Implement 6 checks (worksheet exists, header row, columns, etc.)
- [ ] Test with valid and invalid worksheets
- [ ] Run tests: `python -m pytest tests/ -v`
- [ ] Add docstring examples
- [ ] Commit: `git commit -m "Add sheet validation method"`

**Signs of Success:**
- `validate_worksheet()` returns `(is_valid, errors)`
- Detects missing worksheets
- Detects missing required columns
- Detects duplicate columns
- Tests pass

---

### [ ] 9. Add Column Width Auto-Adjustment (20 min)

**Reference:** cExcelFile_implementation_examples.md → Section 9

Steps:
- [ ] Add `auto_adjust_columns()` method
- [ ] Update `load_from_listofdict()` to call it (add `auto_adjust` parameter)
- [ ] Test with various content lengths
- [ ] Run tests: `python -m pytest tests/ -v`
- [ ] Verify column widths are reasonable (not too narrow, not >50)
- [ ] Commit: `git commit -m "Add column width auto-adjustment"`

**Signs of Success:**
- Columns auto-fit to content
- Column widths capped at reasonable max (50)
- Tests pass
- Excel files are more readable

---

## ✅ Phase 3: Advanced Features (Optional - Week 3+)

Only implement if you need these features. Improvements #10-16 in cExcelFile_improvements.md.

---

## 🧪 Testing Throughout

After EACH improvement:
```bash
# Run all tests
python -m pytest tests/ -v

# Or run specific test file
python -m pytest tests/test_Excel.py -v
```

---

## 📝 Documentation Updates

After each improvement:
- [ ] Update cExcelFile.md API documentation
- [ ] Add docstring examples
- [ ] Update CHANGELOG if one exists

---

## 📊 Final Verification

After all improvements in a phase:

- [ ] All tests pass
- [ ] No regressions in existing functionality
- [ ] Type hints added (Phase 2 only)
- [ ] Code follows project style
- [ ] Docstrings updated
- [ ] Ready for code review/PR

---

## 🎯 Commit Messages Template

Use these templates for clear commit history:

```
# Phase 1 (Foundation)
git commit -m "Extract SprdsheetFldDescriptor to module level"
git commit -m "Add logging instead of print statements"
git commit -m "Implement column freezing via freezecols parameter"
git commit -m "Remove unused placeholder method"

# Phase 2 (Quality)
git commit -m "Add comprehensive type hints"
git commit -m "Standardize CleanProc return value handling"
git commit -m "Add batch-size control for database inserts"
git commit -m "Add sheet validation method"
git commit -m "Add column width auto-adjustment"

# Phase 3 (Advanced)
git commit -m "Add dry-run mode for database operations"
# ... etc
```

---

## 💾 How to Use This Checklist

1. **Print it out** or keep it in an editor
2. **When implementing**, check off items as you complete them
3. **Reference cExcelFile_implementation_examples.md** for code
4. **Run tests after each improvement**
5. **Commit after each successful improvement**

---

## ⏱️ Time Tracking

Track your actual time to compare with estimates:

| Improvement | Est. Time | Actual | Notes |
|-------------|-----------|--------|-------|
| 1. Extract descriptor | 15 min |  |  |
| 2. Add logging | 30 min |  |  |
| 3. Column freezing | 20 min |  |  |
| 4. Remove placeholder | 5 min |  |  |
| **Phase 1 Total** | **1 hr** |  |  |
| 5. Add type hints | 45 min |  |  |
| 6. Standardize returns | 40 min |  |  |
| 7. Batch control | 30 min |  |  |
| 8. Validation | 25 min |  |  |
| 9. Column widths | 20 min |  |  |
| **Phase 2 Total** | **2.5 hrs** |  |  |

---

## 🆘 If You Get Stuck

1. Re-read the relevant section in cExcelFile_improvements.md
2. Check code examples in cExcelFile_implementation_examples.md
3. Run tests to see what failed: `python -m pytest tests/ -v -s`
4. Check cExcelFile.md for API context
5. Verify no syntax errors: `python -m py_compile calvincTools/utils/Excel.py`

---

## 📞 Quick Reference

| Need | File | Section |
|------|------|---------|
| Code example | cExcelFile_implementation_examples.md | Numbered 1-9 |
| Background/why | cExcelFile_improvements.md | Numbered 1-16 |
| Current API | cExcelFile.md | Method reference |
| Quick reminder | cExcelFile_QUICKREF.md | Summary |
| Decision help | cExcelFile_NAVIGATION.md | Decision tree |

---

## ✨ Final Checklist

After completing all improvements you want to implement:

- [ ] All tests pass
- [ ] No type errors
- [ ] API documentation updated
- [ ] Code reviewed
- [ ] Changes committed
- [ ] Pull request created (if applicable)
- [ ] Changes merged

---

**Print this out and keep it nearby when implementing!**

Last Updated: 2026-11-11
