import sqlite3

DB_PATH = "avon_hello.db"

def get_current_campaign_settings():
    """Retrieve the current campaign year and campaign number from the database."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT year, campaign FROM campaign_settings ORDER BY id DESC LIMIT 1")
    result = cursor.fetchone()
    conn.close()
    if result:
        return result  # returns (year, campaign)
    else:
        return (2025, 1)  # default values if none found

def get_representative_info():
    """Retrieve the latest representative info from the database."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT rep_name, rep_address, rep_phone, rep_email, rep_website 
        FROM representative_info 
        ORDER BY id DESC LIMIT 1
    """)
    rep_info = cursor.fetchone()
    conn.close()
    if rep_info:
        return {
            "rep_name": rep_info[0],
            "rep_address": rep_info[1],
            "rep_phone": rep_info[2],
            "rep_email": rep_info[3],
            "rep_website": rep_info[4]
        }
    else:
        return {
            "rep_name": "Representative Name",
            "rep_address": "Representative Address",
            "rep_phone": "Representative Phone",
            "rep_email": "Representative Email",
            "rep_website": "Representative Website"
        }
