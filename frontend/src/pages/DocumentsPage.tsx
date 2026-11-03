import { useEffect, useState } from 'react'
import { Check, FileSearch, UploadCloud } from 'lucide-react'
import { listDocuments, listMines, uploadDocument, verifyDocument, type DocumentRecord, type Mine } from '../services/api'
import { useAuth } from '../contexts/useAuth'

const documentTypes = ['Inspection Report', 'Compliance Certificate', 'Safety Certificate', 'Training Certificate', 'License', 'Evidence', 'Other']

function getOcrStatus(document: DocumentRecord) {
  const status = document.status.toUpperCase()
  if (status === 'OCR_FAILED' || status === 'FAILED') return 'OCR_FAILED'
  if (status === 'OCR_PENDING' || !document.ocr_result) return 'OCR_PENDING'
  return 'OCR_COMPLETED'
}

export default function DocumentsPage() {
  const { user } = useAuth()
  const [documents, setDocuments] = useState<DocumentRecord[]>([])
  const [mines, setMines] = useState<Mine[]>([])
  const [file, setFile] = useState<File | null>(null)
  const [documentType, setDocumentType] = useState(documentTypes[0])
  const [mineId, setMineId] = useState<number | null>(null)
  const [selected, setSelected] = useState<DocumentRecord | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState('')
  const [busy, setBusy] = useState(false)
  const canVerify = ['ADMIN', 'MINE_MANAGER', 'SAFETY_OFFICER', 'AUDITOR'].includes(user?.role ?? '')

  async function load() {
    setIsLoading(true)
    try {
      const [items, availableMines] = await Promise.all([listDocuments(), listMines()])
      setDocuments(items)
      setMines(availableMines)
      setError('')
    } catch {
      setError('Documents could not be loaded.')
    } finally {
      setIsLoading(false)
    }
  }

  useEffect(() => { void load() }, [])

  async function submit() {
    if (!file) {
      setError('Select a document before uploading.')
      return
    }
    const extension = file.name.split('.').pop()?.toLowerCase()
    if (!['pdf', 'jpg', 'jpeg', 'png', 'txt'].includes(extension ?? '')) {
      setError('Unsupported file type. Use PDF, JPG, PNG, or TXT.')
      return
    }
    if (file.size > 10 * 1024 * 1024) {
      setError('File exceeds the 10 MB limit.')
      return
    }
    setBusy(true)
    setError('')
    try {
      const created = await uploadDocument(file, documentType, mineId)
      setDocuments((current) => [created, ...current])
      setSelected(created)
      setFile(null)
    } catch {
      setError('Upload failed. Use a PDF, image, or text document under 10 MB.')
    } finally {
      setBusy(false)
    }
  }

  async function updateVerification(document: DocumentRecord, status: string) {
    setBusy(true)
    try {
      const updated = await verifyDocument(document.id, status)
      setDocuments((current) => current.map((item) => item.id === updated.id ? updated : item))
      setSelected(updated)
    } catch {
      setError('Document verification could not be updated.')
    } finally {
      setBusy(false)
    }
  }

  return <div className="document-management">
    <div className="module-heading"><div><h2>Documents / OCR</h2><p>Upload certificates and evidence with clearly labelled DEMO OCR processing.</p></div><span className="demo-chip">OCR DEMO MODE</span></div>
    <section className="document-upload-panel"><div className="document-upload-heading"><UploadCloud size={22} /><div><h3>Upload document</h3><p>Accepted: PDF, JPG, PNG, or TXT. Maximum size: 10 MB.</p></div></div><div className="document-form-grid"><label>File<input type="file" accept=".pdf,.jpg,.jpeg,.png,.txt" onChange={(event) => setFile(event.target.files?.[0] ?? null)} /></label><label>Document type<select value={documentType} onChange={(event) => setDocumentType(event.target.value)}>{documentTypes.map((type) => <option key={type}>{type}</option>)}</select></label><label>Mine<select value={mineId ?? ''} onChange={(event) => setMineId(event.target.value ? Number(event.target.value) : null)}><option value="">Not linked</option>{mines.map((mine) => <option key={mine.id} value={mine.id}>{mine.mine_name}</option>)}</select></label></div><button className="primary-action" type="button" disabled={busy} onClick={() => void submit()}><UploadCloud size={16} />{busy ? 'Processing...' : 'Upload and run OCR'}</button></section>
    {error && <p className="module-error" role="alert">{error}</p>}
    <div className={`document-layout${selected ? ' has-document-detail' : ''}`}><section className="document-list-panel"><div className="list-heading"><div><p className="eyebrow">Document register</p><h3>{documents.length} records</h3></div><span className="demo-chip">LIVE API</span></div>{isLoading ? <p className="inspection-empty"><span className="module-loading" role="status">Loading documents…</span></p> : documents.length === 0 ? <p className="inspection-empty">No documents uploaded yet.</p> : <div className="document-table-wrap"><table className="document-table"><thead><tr><th>Document name</th><th>Document type</th><th>Mine</th><th>OCR status</th><th>Actions</th></tr></thead><tbody>{documents.map((document) => { const ocrStatus = getOcrStatus(document); return <tr key={document.id} className={selected?.id === document.id ? 'selected' : undefined}><td><button className="document-name-button" type="button" title={document.file_name} onClick={() => setSelected(document)}><FileSearch size={16} /><span>{document.file_name}</span></button></td><td>{document.document_type}</td><td>{document.mine_name ?? 'Unlinked'}</td><td><span className={`ocr-status-badge ocr-status-${ocrStatus.toLowerCase()}`}>{ocrStatus}</span></td><td><button className="document-view-button" type="button" onClick={() => setSelected(document)}>{selected?.id === document.id ? 'Selected' : 'View'}</button></td></tr> })}</tbody></table></div>}</section>{selected && <section className="document-detail-panel"><p className="eyebrow">OCR result / {selected.ocr_result?.verification_status ?? 'PENDING'}</p><h3>{selected.file_name}</h3><p>{selected.document_type} / {selected.mine_name ?? 'No mine linked'}</p><div className="document-confidence"><strong>{Math.round((selected.ocr_result?.confidence ?? 0) * 100)}%</strong><span>OCR confidence</span></div><h4>Detected fields</h4><pre>{selected.ocr_result?.detected_fields ?? '{}'} </pre><h4>Extracted text</h4><p className="ocr-text">{selected.ocr_result?.extracted_text ?? 'No OCR result available.'}</p>{canVerify && selected.status !== 'VERIFIED' && <div className="document-actions"><button className="primary-action" type="button" disabled={busy} onClick={() => void updateVerification(selected, 'VERIFIED')}><Check size={16} />Verify document</button><button type="button" disabled={busy} onClick={() => void updateVerification(selected, 'REJECTED')}>Reject</button></div>}</section>}</div>
  </div>
}
