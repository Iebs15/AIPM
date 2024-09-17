import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import {createBrowserRouter, RouterProvider} from 'react-router-dom'
import App from './App.jsx'
import './index.css'
import Authenticate from './pages/Authenticate.jsx'
import Header from './components/Header.jsx'
import Layout from './components/Layout.jsx'
import ProteinStability from './pages/ProteinStability.jsx'
import DrugRepurposing from './pages/DrugRepurposing.jsx'
import PrivateRoute from './PrivateRoute.jsx'
import Home from './pages/Home.jsx'
import CTO from './pages/CTO.jsx'


const router = createBrowserRouter([
  {
    path: '/',
    element: <Authenticate/>
  },
  {
    path: '/home',
    element: (
      <PrivateRoute>
        <Layout>
          <Home />
        </Layout>
      </PrivateRoute>
    )
  },
  {
    path: '/layout',
    element: <Layout/>
  },
  {
    path: "/protein-stability",
    element: (
      <PrivateRoute>
        <Layout>
          <ProteinStability />
        </Layout>
      </PrivateRoute>
    )
  },
  {
    path: "/drug-repurposing",
    element: (
      <PrivateRoute>
        <Layout>
          <DrugRepurposing />
        </Layout>
      </PrivateRoute>
    )
  },
  {
    path: "/cto",
    element: (
      <PrivateRoute>
        <Layout>
          <CTO />
        </Layout>
      </PrivateRoute>
    )
  },
])

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <RouterProvider router={router} />
  </StrictMode>,
)
