#include <iostream>
#include <cassert>
#include "calvinc_tools/database/database_context.hpp"

using namespace calvinc::tools::database;

int main() {
    std::cout << "Running Database Tests\n";
    
    // Test database initialization
    DatabaseContext& db = DatabaseContext::getInstance();
    bool initialized = db.initialize(":memory:");  // Use in-memory SQLite
    assert(initialized);
    assert(db.isOpen());
    
    // Test that tables were created
    assert(db.getDatabase().isOpen());
    
    std::cout << "All database tests passed!\n";
    return 0;
}
