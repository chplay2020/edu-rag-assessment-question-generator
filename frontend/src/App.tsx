import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthGuard } from './routes/AuthGuard';
import { MainLayout } from './layouts/MainLayout';
import { Login } from './pages/Login';
import { Dashboard } from './pages/Dashboard';
import { Courses } from './pages/Courses';
import { CourseDetail } from './pages/CourseDetail';
import { CourseMaterials } from './pages/CourseMaterials';
import { MaterialDetail } from './pages/MaterialDetail';
import { GenerateQuestions } from './pages/GenerateQuestions';
import { JobResult } from './pages/JobResult';
import { ReviewDashboard } from './pages/ReviewDashboard';
import { QuestionBank } from './pages/QuestionBank';

function App() {
  return (
    <Router>
      <Routes>
        {/* Public Routes */}
        <Route path="/login" element={<Login />} />

        {/* Protected Routes */}
        <Route element={<AuthGuard />}>
          <Route element={<MainLayout />}>
            <Route path="/" element={<Dashboard />} />
            <Route path="/questions" element={<ReviewDashboard />} />
            <Route path="/question-bank" element={<QuestionBank />} />
            <Route path="/courses" element={<Courses />} />
            <Route path="/courses/:id" element={<CourseDetail />} />
            <Route path="/courses/:id/materials" element={<CourseMaterials />} />
            <Route path="/courses/:courseId/materials/:materialId" element={<MaterialDetail />} />
            <Route path="/courses/:courseId/materials/:materialId/generate" element={<GenerateQuestions />} />
            <Route path="/courses/:courseId/materials/:materialId/jobs/:jobId" element={<JobResult />} />
          </Route>
        </Route>

        {/* Fallback */}
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </Router>
  );
}

export default App;
