import { Navigate, Route, BrowserRouter as Router, Routes } from "react-router-dom";
import { Toaster } from "react-hot-toast";

import { AppLayout } from "./components/layout/AppLayout";
import { ProtectedRoute } from "./components/layout/ProtectedRoute";
import { LoginPage } from "./pages/auth/LoginPage";
import { RegisterPage } from "./pages/auth/RegisterPage";
import { PlaceholderPage } from "./pages/common/PlaceholderPage";
import { JuryLeaderboardPage } from "./pages/jury/JuryLeaderboardPage";
import { ReviewDetailPage } from "./pages/jury/ReviewDetailPage";
import { ReviewListPage } from "./pages/jury/ReviewListPage";
import { AlgoTasksPage } from "./pages/participant/AlgoTasksPage";
import { HackathonListPage } from "./pages/participant/HackathonListPage";
import { ResultsPage } from "./pages/participant/ResultsPage";
import { SubmissionPage } from "./pages/participant/SubmissionPage";
import { TeamPage } from "./pages/participant/TeamPage";

function App() {
  return (
    <Router>
      <Routes>
        <Route element={<LoginPage />} path="/login" />
        <Route element={<RegisterPage />} path="/register" />

        <Route element={<ProtectedRoute roles={["participant"]} />}>
          <Route element={<AppLayout />}>
            <Route element={<HackathonListPage />} path="/participant/hackathons" />
            <Route element={<TeamPage />} path="/participant/team" />
            <Route element={<SubmissionPage />} path="/participant/submission" />
            <Route element={<ResultsPage />} path="/participant/results" />
            <Route element={<AlgoTasksPage />} path="/participant/algo" />
          </Route>
        </Route>

        <Route element={<ProtectedRoute roles={["jury"]} />}>
          <Route element={<AppLayout />}>
            <Route element={<ReviewListPage />} path="/jury/reviews" />
            <Route element={<ReviewDetailPage />} path="/jury/reviews/:submissionId" />
            <Route element={<JuryLeaderboardPage />} path="/jury/leaderboard" />
          </Route>
        </Route>

        <Route element={<ProtectedRoute roles={["organizer"]} />}>
          <Route element={<AppLayout />}>
            <Route element={<PlaceholderPage description="Настройки хакатона, даты и смена статуса." title="Управление хакатоном" />} path="/organizer/hackathon" />
            <Route element={<PlaceholderPage description="Критерии, веса, типы автопроверок и экспертных оценок." title="Критерии оценки" />} path="/organizer/criteria" />
            <Route element={<PlaceholderPage description="Список команд, участники и прогресс решений." title="Команды" />} path="/organizer/teams" />
            <Route element={<PlaceholderPage description="Создание задач, тесты и результаты попыток." title="Алго-задачи" />} path="/organizer/algo" />
            <Route element={<PlaceholderPage description="Финальная таблица результатов и экспорт CSV." title="Лидерборд" />} path="/organizer/leaderboard" />
          </Route>
        </Route>

        <Route element={<Navigate replace to="/login" />} path="*" />
      </Routes>
      <Toaster position="bottom-right" />
    </Router>
  );
}

export default App;
