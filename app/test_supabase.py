from supabase import create_client
url = "https://kgojizbibruhdwcqjxqc.supabase.co"
key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imtnb2ppemJpYnJ1aGR3Y3FqeHFjIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzgwNTA1OTAsImV4cCI6MjA5MzYyNjU5MH0.bWGfsJUvJ6EuiunV-FjDzQKk8AMPnmYz7D52gmyluVY"
supabase = create_client(url, key)
res = supabase.table("alerts").select("*").execute()
print(res)