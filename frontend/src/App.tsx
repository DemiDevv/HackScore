import { Navigate, Route, BrowserRouter as Router, Routes } from "react-router-dom";
import { Toaster } from "react-hot-toast";

import { AppLayout } from "./components/layout/AppLayout";
import { ProtectedRoute } from "./components/layout/ProtectedRoute";
import { LoginPage } from "./pages/auth/LoginPage";
import { RegisterPage } from "./pages/auth/RegisterPage";
import { PlaceholderPage } from "./pages/common/PlaceholderPage";

function App() {
  return (
    <Router>
      <Routes>
        <Route element={<LoginPage />} path="/login" />
        <Route element={<RegisterPage />} path="/register" />

        <Route element={<ProtectedRoute roles={["participant"]} />}>
          <Route element={<AppLayout />}>
            <Route element={<PlaceholderPage description="Список хакатонов участника, команды и статусы отправки решений." title="Мои хакатоны" />} path="/participant/hackathons" />
            <Route element={<PlaceholderPage description="Команда, участники и приглашения по email." title="Моя команда" />} path="/participant/team" />
            <Route element={<PlaceholderPage description="Загрузка репозитория, документации, презентации и скринкаста." title="Загрузка решения" />} path="/participant/submission" />
            <Route element={<PlaceholderPage description="Автоматические проверки, экспертные критерии и итоговый балл." title="Результаты" />} path="/participant/results" />
            <Route element={<PlaceholderPage description="Алгоритмические задачи, редактор кода и мои попытки." title="Алго-задачи" />} path="/participant/algo" />
          </Route>
        </Route>

        <Route element={<ProtectedRoute roles={["jury"]} />}>
          <Route element={<AppLayout />}>
            <Route element={<PlaceholderPage description="Таблица решений команд, фильтры и переход к оценке." title="Решения команд" />} path="/jury/reviews" />
            <Route element={<PlaceholderPage description="Итоговая таблица команд по автоматическим и экспертным баллам." title="Лидерборд" />} path="/jury/leaderboard" />
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
