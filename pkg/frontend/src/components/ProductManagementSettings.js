import React, { useEffect, useState } from 'react';
import {
  Box, Typography, TextField, Button, CircularProgress, IconButton, Paper, Snackbar, Alert
} from '@mui/material';
import { Add, Delete, Refresh } from '@mui/icons-material';

const darkCard = {
  backgroundColor: '#1F1B24',
  borderRadius: '16px',
  padding: '2rem',
  boxShadow: '0 4px 20px rgba(33, 150, 243, 0.1)',
  marginBottom: '2rem',
  border: '1px solid #2A3B4D',
  color: '#fff'
};

function ProductManagementSettings() {
  const [products, setProducts] = useState([]);
  const [responsibles, setResponsibles] = useState({});
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [extracting, setExtracting] = useState(false);

  // Default owner info (should match backend fallback)
  const [defaultOwnerName, setDefaultOwnerName] = useState('Default Owner');
  const [defaultOwnerEmail, setDefaultOwnerEmail] = useState('default-owner@yourcompany.com');
  const [defaultOwnerSaving, setDefaultOwnerSaving] = useState(false);

  // Fetch products, responsibles, and default owner
  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      try {
        const prodRes = await fetch('/api/products');
        const prodData = await prodRes.json();
        setProducts(prodData.products || []);
        // Fetch responsible for each product
        const responsiblesObj = {};
        for (const p of prodData.products || []) {
          const respRes = await fetch(`/api/responsible_person?product_name=${encodeURIComponent(p)}`);
          const respData = await respRes.json();
          responsiblesObj[p] = respData || { name: '', email: '' };
        }
        setResponsibles(responsiblesObj);
        // Fetch default responsible person
        const defRes = await fetch('/api/default_responsible_person');
        if (defRes.ok) {
          const defData = await defRes.json();
          setDefaultOwnerName(defData.name || 'Default Owner');
          setDefaultOwnerEmail(defData.email || 'default-owner@yourcompany.com');
        }
      } catch (err) {
        setError('Failed to load products or responsibles');
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  // Extract products from backend (LLM/Chroma)
  const handleExtractProducts = async () => {
    setExtracting(true);
    setError('');
    setSuccess('');
    try {
      // Get company info
      const infoRes = await fetch('/api/company_info');
      const infoData = await infoRes.json();
      const companyInfo = infoData.info || '';
      // Call backend to extract products (simulate via POST /api/products with {extract: true})
      const res = await fetch('/api/products', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ extract: true, company_info: companyInfo })
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.error || 'Extraction failed');
      setProducts(data.products || []);
      setSuccess('Products extracted from company info!');
    } catch (err) {
      setError(err.message || 'Failed to extract products');
    } finally {
      setExtracting(false);
    }
  };

  // Save products and responsibles
  const handleSave = async () => {
    setSaving(true);
    setError('');
    setSuccess('');
    try {
      // Save products
      await fetch('/api/products', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ products })
      });
      // Save responsibles
      for (const p of products) {
        const person = responsibles[p] || { name: '', email: '' };
        await fetch('/api/responsible_person', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ product_name: p, person })
        });
      }
      setSuccess('Saved successfully!');
    } catch (err) {
      setError('Failed to save changes');
    } finally {
      setSaving(false);
    }
  };

  // Save default responsible person
  const handleSaveDefaultOwner = async () => {
    setDefaultOwnerSaving(true);
    setError('');
    setSuccess('');
    try {
      const res = await fetch('/api/default_responsible_person', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name: defaultOwnerName, email: defaultOwnerEmail })
      });
      if (!res.ok) throw new Error('Failed to save default responsible person');
      setSuccess('Default responsible person updated!');
    } catch (err) {
      setError('Failed to save default responsible person');
    } finally {
      setDefaultOwnerSaving(false);
    }
  };

  // Add/remove product
  const handleAddProduct = () => {
    setProducts([...products, '']);
  };
  const handleRemoveProduct = (idx) => {
    const prod = products[idx];
    setProducts(products.filter((_, i) => i !== idx));
    const newResp = { ...responsibles };
    delete newResp[prod];
    setResponsibles(newResp);
  };

  // Edit product name
  const handleProductChange = (idx, value) => {
    const oldName = products[idx];
    const newProducts = [...products];
    newProducts[idx] = value;
    setProducts(newProducts);
    // Move responsible if name changes
    if (oldName && oldName !== value && responsibles[oldName]) {
      setResponsibles((prev) => {
        const updated = { ...prev };
        updated[value] = updated[oldName];
        delete updated[oldName];
        return updated;
      });
    }
  };

  // Edit responsible person
  const handleResponsibleChange = (prod, field, value) => {
    setResponsibles((prev) => ({
      ...prev,
      [prod]: { ...prev[prod], [field]: value }
    }));
  };

  return (
    <Paper sx={darkCard}>
      <Typography variant="h5" sx={{ mb: 2, color: '#fff' }}>Products & Responsible Persons</Typography>
      <Typography variant="body2" sx={{ mb: 2, color: '#a0aec0' }}>
        Manage your product list and assign a responsible person (name & email) for each product. You can extract products from your company info, edit, and save.
      </Typography>
      {/* Editable default owner info */}
      <Box sx={{ mb: 2, p: 2, background: '#232323', borderRadius: 2 }}>
        <Typography variant="subtitle2" sx={{ color: '#ff9800', mb: 1 }}>
          Default Responsible Person (used if none is set for a product):
        </Typography>
        <Box sx={{ display: 'flex', gap: 2, alignItems: 'center', mb: 1 }}>
          <TextField
            label="Default Name"
            value={defaultOwnerName}
            onChange={e => setDefaultOwnerName(e.target.value)}
            size="small"
            sx={{ input: { color: '#fff' }, label: { color: '#a0aec0' } }}
          />
          <TextField
            label="Default Email"
            value={defaultOwnerEmail}
            onChange={e => setDefaultOwnerEmail(e.target.value)}
            size="small"
            sx={{ input: { color: '#fff' }, label: { color: '#a0aec0' } }}
          />
          <Button
            variant="contained"
            onClick={handleSaveDefaultOwner}
            disabled={defaultOwnerSaving}
            sx={{ background: '#2196F3', color: '#fff' }}
          >
            {defaultOwnerSaving ? 'Saving...' : 'Save'}
          </Button>
        </Box>
        <Typography variant="body2" sx={{ color: '#fff' }}>
          Name: <b>{defaultOwnerName}</b> &nbsp; | &nbsp; Email: <b>{defaultOwnerEmail}</b>
        </Typography>
      </Box>
      <Box sx={{ display: 'flex', gap: 2, mb: 2 }}>
        <Button
          variant="contained"
          startIcon={<Refresh />}
          onClick={handleExtractProducts}
          disabled={extracting}
        >
          {extracting ? 'Extracting...' : 'Extract Products from Company Info'}
        </Button>
        <Button
          variant="contained"
          startIcon={<Add />}
          onClick={handleAddProduct}
        >
          Add Product
        </Button>
      </Box>
      {loading ? (
        <Box sx={{ textAlign: 'center', py: 4 }}>
          <CircularProgress />
        </Box>
      ) : (
        <Box>
          {products.length === 0 && (
            <Typography variant="body2" sx={{ color: '#a0aec0', mb: 2 }}>
              No products found. Extract from company info or add manually.
            </Typography>
          )}
          {products.map((prod, idx) => (
            <Box key={idx} sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2 }}>
              <TextField
                label="Product Name"
                value={prod}
                onChange={e => handleProductChange(idx, e.target.value)}
                sx={{ flex: 2 }}
                size="small"
                InputProps={{ style: { color: '#fff' } }}
                InputLabelProps={{ style: { color: '#a0aec0' } }}
              />
              <TextField
                label="Responsible Name"
                value={responsibles[prod]?.name || ''}
                onChange={e => handleResponsibleChange(prod, 'name', e.target.value)}
                sx={{ flex: 2 }}
                size="small"
                InputProps={{ style: { color: '#fff' } }}
                InputLabelProps={{ style: { color: '#a0aec0' } }}
              />
              <TextField
                label="Responsible Email"
                value={responsibles[prod]?.email || ''}
                onChange={e => handleResponsibleChange(prod, 'email', e.target.value)}
                sx={{ flex: 3 }}
                size="small"
                InputProps={{ style: { color: '#fff' } }}
                InputLabelProps={{ style: { color: '#a0aec0' } }}
              />
              <IconButton onClick={() => handleRemoveProduct(idx)} color="error">
                <Delete />
              </IconButton>
            </Box>
          ))}
        </Box>
      )}
      <Box sx={{ display: 'flex', justifyContent: 'flex-end', mt: 3 }}>
        <Button
          variant="contained"
          color="primary"
          onClick={handleSave}
          disabled={saving}
        >
          {saving ? 'Saving...' : 'Save Changes'}
        </Button>
      </Box>
      <Snackbar open={!!error} autoHideDuration={6000} onClose={() => setError('')} anchorOrigin={{ vertical: 'top', horizontal: 'right' }}>
        <Alert onClose={() => setError('')} severity="error" sx={{ width: '100%', color: '#fff', backgroundColor: '#d32f2f' }}>{error}</Alert>
      </Snackbar>
      <Snackbar open={!!success} autoHideDuration={6000} onClose={() => setSuccess('')} anchorOrigin={{ vertical: 'top', horizontal: 'right' }}>
        <Alert onClose={() => setSuccess('')} severity="success" sx={{ width: '100%', color: '#fff', backgroundColor: '#388e3c' }}>{success}</Alert>
      </Snackbar>
    </Paper>
  );
}

export default ProductManagementSettings; 