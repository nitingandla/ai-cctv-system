from supabase import create_client
url = "https://kgojizbibruhdwcqjxqc.supabase.co"
key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imtnb2ppemJpYnJ1aGR3Y3FqeHFjIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzgwNTA1OTAsImV4cCI6MjA5MzYyNjU5MH0.bWGfsJUvJ6EuiunV-FjDzQKk8AMPnmYz7D52gmyluVY"
supabase = create_client(url, key)
def insert_alert(event_type, person_count):
    data = {
        "event_type": event_type,
        "person_count": person_count
    }
    response = supabase.table("alerts").insert(data).execute()
    print("DB Response:", response)