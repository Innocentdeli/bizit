import sqlite3

def seed_geo_data():
    conn = sqlite3.connect('./bizit_pulse.db')
    cursor = conn.cursor()
    
    # Update existing businesses with coordinates
    updates = [
        ("6.5244", "3.3792", "b-1"),     # Lagos Tech Hub (approx)
        ("6.4549", "3.4246", "b-101"),   # Victoria Island
        ("9.0765", "7.3986", "b-2"),     # Abuja Wuse
        ("6.6018", "3.3515", "b-102")    # Ikeja
    ]
    
    for lat, lng, b_id in updates:
        cursor.execute("UPDATE businesses SET lat=?, lng=? WHERE id=?", (lat, lng, b_id))
    
    conn.commit()
    print(f"✅ Successfully seeded {len(updates)} records with Geo-Spatial data.")
    conn.close()

if __name__ == "__main__":
    seed_geo_data()
