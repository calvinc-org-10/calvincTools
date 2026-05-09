#pragma once

#include <QString>
#include <QSqlDatabase>
#include <memory>

namespace calvinc::tools::database {

/**
 * DatabaseContext manages SQLite database connections and initialization.
 * Singleton pattern for application-wide database access.
 */
class DatabaseContext {
private:
    static std::unique_ptr<DatabaseContext> instance_;
    QSqlDatabase db_;
    QString dbPath_;
    bool initialized_;
    
    DatabaseContext();
    DatabaseContext(const DatabaseContext&) = delete;
    DatabaseContext& operator=(const DatabaseContext&) = delete;

public:
    /**
     * Get the singleton instance of the database context.
     */
    static DatabaseContext& getInstance();
    
    /**
     * Initialize the database with the specified path.
     * Creates tables if they don't exist.
     * 
     * @param dbPath Path to the SQLite database file. 
     *               If empty, uses default "cMenudb.sqlite".
     * @return true if initialization succeeded, false otherwise.
     */
    bool initialize(const QString& dbPath = "cMenudb.sqlite");
    
    /**
     * Get the QSqlDatabase object for this context.
     */
    QSqlDatabase getDatabase();
    
    /**
     * Check if the database is initialized and open.
     */
    bool isOpen() const;
    
    /**
     * Close the database connection.
     */
    void close();
    
    /**
     * Create all tables if they don't exist.
     * @return true if all tables were created or already existed.
     */
    bool createTables();
    
    /**
     * Get the path to the database file.
     */
    const QString& getDbPath() const { return dbPath_; }
};

}  // namespace calvinc::tools::database
