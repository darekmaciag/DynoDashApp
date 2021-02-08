from database import Database

def get_sensor_types():
    """Get a list of different types of sensors"""
    sql = """
        --Get the labels and underlying values for the dropdown menu "children"
        SELECT 
            distinct 
            name as label, 
            id as value
        FROM sensors;
    """
    with Database() as db:
        aa = db.query(sql)
        db.close 
        return print(aa)

get_sensor_types()