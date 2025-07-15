// src/pages/Dashboard.jsx
import React from "react";
import EntityXStateMonitor from "../components/EntityXStateMonitor";

const Dashboard = () => {
  return (
    <div className="p-8">
      <h1 className="text-3xl font-bold mb-8 text-green-400">🌿 Garden 대시보드</h1>

      {/* AI 상태 모니터링 시스템 삽입 */}
      <EntityXStateMonitor />

      {/* 대시보드의 다른 위젯/그래프/정보 등 추가 */}
    </div>
  );
};

export default Dashboard;