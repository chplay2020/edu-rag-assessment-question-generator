import React, { useEffect, useState } from 'react';
import { motion } from 'motion/react';
import { 
  GraduationCap, 
  FileArrowUp, 
  Sparkle, 
  CheckCircle, 
  Warning, 
  ArrowUpRight 
} from '@phosphor-icons/react';
import { 
  PieChart, 
  Pie, 
  Cell, 
  BarChart, 
  Bar, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip as RechartsTooltip, 
  Legend, 
  ResponsiveContainer 
} from 'recharts';
import { getDashboardSummary, type DashboardSummary } from '../services/dashboardApi';

// Updated Color Palette based on design
const COLORS = ['#f59e0b', '#3b82f6', '#10b981', '#ef4444', '#8b5cf6'];
const STATUS_COLORS: Record<string, string> = {
  'Đã duyệt': '#10b981', // emerald-500
  'Từ chối': '#ef4444',  // red-500
  'Chờ duyệt': '#f59e0b', // amber-500
  'Bản nháp': '#4f46e5',  // indigo-600
};

export const Dashboard: React.FC = () => {
  const [data, setData] = useState<DashboardSummary | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const result = await getDashboardSummary();
        setData(result);
      } catch (error) {
        console.error("Lỗi khi tải dữ liệu dashboard:", error);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  const containerVariants = {
    hidden: { opacity: 0 },
    show: { opacity: 1, transition: { staggerChildren: 0.05 } }
  } as const;

  const itemVariants = {
    hidden: { opacity: 0, y: 12 },
    show: { opacity: 1, y: 0, transition: { type: "spring" as const, stiffness: 400, damping: 30 } }
  } as const;

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="flex flex-col items-center gap-3">
          <div className="w-6 h-6 border-2 border-zinc-900 border-t-transparent rounded-full animate-spin" />
          <p className="text-sm font-medium text-zinc-500">Đang đồng bộ dữ liệu...</p>
        </div>
      </div>
    );
  }

  if (!data) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <p className="text-sm font-medium text-zinc-500">Không có dữ liệu hiển thị.</p>
      </div>
    );
  }

  const statusMap: Record<string, string> = {
    'approved': 'Đã duyệt',
    'rejected': 'Từ chối',
    'draft': 'Bản nháp',
    'review_required': 'Chờ duyệt'
  };
  const diffMap: Record<string, string> = {
    'easy': 'Dễ',
    'medium': 'Vừa',
    'hard': 'Khó'
  };

  const chartStatus = data.questions_by_status?.length > 0 
    ? data.questions_by_status.map(d => ({ ...d, name: statusMap[d.name] || d.name }))
    : [{ name: 'Bản nháp', value: 10 }];

  const chartDiff = data.questions_by_difficulty?.length > 0
    ? data.questions_by_difficulty.map(d => ({ ...d, name: diffMap[d.name] || d.name }))
    : [{ name: 'Vừa', value: 10 }];

  const chartBloom = data.questions_by_bloom?.length > 0
    ? data.questions_by_bloom
    : [
        { name: 'understand', value: 10 }
      ];

  return (
    <motion.div
      className="p-6 md:p-8 lg:p-10 w-full mx-auto flex flex-col gap-8"
      variants={containerVariants}
      initial="hidden"
      animate="show"
    >
      {/* Header */}
      <motion.div variants={itemVariants} className="flex flex-col gap-1.5">
        <h1 className="text-2xl md:text-3xl font-semibold tracking-tight text-zinc-900 dark:text-zinc-50">
          Tổng quan
        </h1>
        <p className="text-sm md:text-base text-zinc-500 dark:text-zinc-400 max-w-2xl">
          Thống kê tình hình tạo và duyệt câu hỏi của bạn.
        </p>
      </motion.div>

      {/* Stats Grid - 6 Columns */}
      <motion.div
        className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4"
        variants={containerVariants}
      >
        <StatCard 
          title="Tài liệu" 
          value={data.total_materials} 
          icon={<FileArrowUp size={24} weight="regular" />} 
          iconBgClass="bg-indigo-50"
          iconColorClass="text-indigo-500"
        />
        <StatCard 
          title="Tiến trình (Jobs)" 
          value={data.total_jobs} 
          icon={<ArrowUpRight size={24} weight="regular" />} 
          iconBgClass="bg-cyan-50"
          iconColorClass="text-cyan-500"
        />
        <StatCard 
          title="Câu hỏi sinh ra" 
          value={data.total_generated_questions} 
          icon={<Sparkle size={24} weight="regular" />} 
          iconBgClass="bg-purple-50"
          iconColorClass="text-purple-500"
        />
        <StatCard 
          title="Câu hỏi Đã duyệt" 
          value={data.total_approved_questions} 
          icon={<CheckCircle size={24} weight="regular" />} 
          iconBgClass="bg-emerald-50"
          iconColorClass="text-emerald-500"
        />
        <StatCard 
          title="Câu hỏi Từ chối" 
          value={data.total_rejected_questions} 
          icon={<Warning size={24} weight="regular" />} 
          iconBgClass="bg-amber-50"
          iconColorClass="text-amber-500"
        />
        <StatCard 
          title="Điểm AI TB" 
          value={data.validation_avg_score} 
          icon={<GraduationCap size={24} weight="regular" />} 
          iconBgClass="bg-pink-50"
          iconColorClass="text-pink-500"
          isFloat 
        />
      </motion.div>

      {/* Charts Grid - First Row (Pies) */}
      <motion.div 
        className="flex flex-col md:flex-row gap-5"
        variants={containerVariants}
      >
        {/* Status Chart */}
        <motion.div variants={itemVariants} className="w-full md:w-1/3 xl:w-1/4 border border-zinc-200 dark:border-zinc-800 bg-white dark:bg-zinc-900 rounded-2xl p-5 md:p-6 shadow-sm flex flex-col">
          <div className="mb-6">
            <h3 className="text-base font-semibold text-zinc-900 dark:text-zinc-100">Trạng thái câu hỏi</h3>
          </div>
          <div className="flex-1 min-h-[220px]">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={chartStatus}
                  cx="50%"
                  cy="50%"
                  innerRadius={50}
                  outerRadius={90}
                  paddingAngle={2}
                  dataKey="value"
                  stroke="none"
                >
                  {chartStatus.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={STATUS_COLORS[entry.name] || COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <RechartsTooltip 
                  contentStyle={{ borderRadius: '8px', border: 'none', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)' }}
                  itemStyle={{ color: '#18181b', fontSize: '14px', fontWeight: 500 }}
                />
                <Legend iconType="square" wrapperStyle={{ fontSize: '13px', paddingTop: '10px' }} />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </motion.div>

        {/* Difficulty Chart */}
        <motion.div variants={itemVariants} className="w-full md:w-1/3 xl:w-1/4 border border-zinc-200 dark:border-zinc-800 bg-white dark:bg-zinc-900 rounded-2xl p-5 md:p-6 shadow-sm flex flex-col">
          <div className="mb-6">
            <h3 className="text-base font-semibold text-zinc-900 dark:text-zinc-100">Mức độ khó</h3>
          </div>
          <div className="flex-1 min-h-[220px]">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={chartDiff}
                  cx="50%"
                  cy="50%"
                  outerRadius={90}
                  dataKey="value"
                  stroke="none"
                  label
                >
                  {chartDiff.map((_, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <RechartsTooltip 
                  contentStyle={{ borderRadius: '8px', border: 'none', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)' }}
                />
                <Legend iconType="square" wrapperStyle={{ fontSize: '13px', paddingTop: '10px' }} />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </motion.div>
      </motion.div>

      {/* Bloom Chart */}
      <motion.div variants={itemVariants} className="w-full border border-zinc-200 dark:border-zinc-800 bg-white dark:bg-zinc-900 rounded-2xl p-5 md:p-6 shadow-sm flex flex-col">
        <div className="mb-6">
          <h3 className="text-base font-semibold text-zinc-900 dark:text-zinc-100">Thang đo Bloom</h3>
        </div>
        <div className="w-full h-[300px] mt-4">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={chartBloom} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#e4e4e7" />
              <XAxis 
                dataKey="name" 
                axisLine={false} 
                tickLine={false} 
                tick={{ fontSize: 13, fill: '#71717a' }} 
                dy={10}
              />
              <YAxis 
                axisLine={false} 
                tickLine={false} 
                tick={{ fontSize: 13, fill: '#71717a' }} 
              />
              <RechartsTooltip 
                cursor={{ fill: '#f4f4f5' }}
                contentStyle={{ borderRadius: '8px', border: 'none', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)' }}
              />
              <Bar 
                dataKey="value" 
                fill="#4f46e5" 
                radius={[4, 4, 0, 0]}
                barSize={120}
                name="Số câu hỏi"
              />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </motion.div>
    </motion.div>
  );
};

// Premium Stat Card
interface StatCardProps {
  title: string;
  value: number;
  icon: React.ReactNode;
  iconBgClass?: string;
  iconColorClass?: string;
  isFloat?: boolean;
}

const StatCard: React.FC<StatCardProps> = ({ 
  title, 
  value, 
  icon, 
  iconBgClass = "bg-zinc-100 dark:bg-zinc-800",
  iconColorClass = "text-zinc-600 dark:text-zinc-300",
  isFloat = false 
}) => {
  const displayValue = isFloat ? Number(value).toFixed(1) : value.toLocaleString('en-US');
  
  return (
    <motion.div
      whileHover={{ y: -2, transition: { duration: 0.2 } }}
      className="flex flex-col p-4 md:p-5 min-h-[140px] justify-center bg-white dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 rounded-2xl shadow-sm relative overflow-hidden group"
    >
      <div className="flex justify-between items-start mb-2">
        <h3 className="text-[14px] font-medium text-zinc-600 dark:text-zinc-400">
          {title}
        </h3>
        <div className={`p-2 rounded-xl ${iconBgClass} ${iconColorClass}`}>
          {icon}
        </div>
      </div>
      
      <div className="flex items-baseline gap-3">
        <p className="text-4xl font-bold tracking-tight text-zinc-900 dark:text-zinc-50">
          {displayValue}
        </p>
      </div>
    </motion.div>
  );
};
