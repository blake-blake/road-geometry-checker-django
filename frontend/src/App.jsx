import { useState } from "react"

function App() {
  const [file, setFile] = useState(null)
  const [speed, setSpeed] = useState(100)
  const [emax, setEmax] = useState(6)
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)


  async function handleSubmit(e) {
    e.preventDefault()
    if (!file) return

    setLoading(true)
    setError(null)
    setResult(null)

    const form = new FormData()
    form.append('file', file)
    form.append('design_speed', speed)
    form.append('emax', emax)

    try {
      const res = await fetch('/api/check/', {method: 'POST', body: form})
      const data = await res.json()
      if (!res.ok) throw new Error(data.error || "Request failed")
      setResult(data)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }

  }


  return (
    <div>
      <h1>Road Geometry Checker</h1>
      <p>Selected file: {file ? file.name : 'none'}</p>
    
      <form onSubmit={handleSubmit}>
        <input type ="file" onChange={e => setFile(e.target.files[0])} />
        <select value={speed} onChange={e => setSpeed(Number(e.target.value))}>
          {[40, 50, 60, 70, 80, 100].map(s => (<option key={s} value ={s}>
            {s} km/h
            </option>))}
        </select>

        <select value={emax} onChange={e => setEmax(Number(e.target.value))}>
          <option value={6}>emax 6%</option>
          <option value={7}>emax 7%</option>
          <option value={10}>emax 10%</option>
        </select>
        <button type="submit" disable={loading || !file}>
          {loading ? 'Checking...' : 'Run Checks'}
        </button>
      </form>

      {error && <p style={{ color: 'red'}}>{error}</p>}

      {result && (
        <div>
          <h2>{result.alignment.name}</h2>
          <p> Chainage {result.alignment.start_chainage} - {result.alignment.end_chainage}</p>
          <p> Pass: {result.summary.pass} | Fail: {result.summary.faul} | Warning: {result.summary.warning}</p> 

          <table>
            <thead>
              <tr> 
                <th>Element</th>
                <th>Check</th>
                <th>Value</th>
                <th>Limit</th>
                <th>Status</th>
                <th>Clause</th>
              </tr>
            </thead>
            <tbody>
              {result.results.map(r => (
                <tr key={r.id}>
                  <td>{r.element}</td>
                  <td>{r.check}</td>
                  <td>{r.value}</td>
                  <td>{r.limit}</td>
                  <td>{r.status.toUpperCase()}</td>
                  <td>{r.clause}</td>
                </tr>
              ))}
            </tbody>
          </table>

        </div>
      )}

    </div>
  )
}

export default App