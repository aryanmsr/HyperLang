export async function GET() {
  const response = await fetch('http://127.0.0.1:8000/api/data');
  const data = await response.json();

  return Response.json(data);
}
