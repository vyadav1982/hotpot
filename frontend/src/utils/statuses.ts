import {
  CheckCircle,
  Clock,
  XCircle,
  Save,
  Send,
  DollarSign,
  CircleDot,
  AlertCircle,
  FileQuestion,
  UserCheck,
  CheckSquare,
} from 'lucide-react';

export const statuses = [
  {
    value: 'Approved',
    label: 'Approved',
    icon: CheckCircle,
    colors: {
      bg: 'bg-green-100',
      text: 'text-green-800',
      border: 'border-green-200',
    },
  },
  {
    value: 'Pending',
    label: 'Pending',
    icon: Clock,
    colors: {
      bg: 'bg-yellow-100',
      text: 'text-yellow-800',
      border: 'border-yellow-200',
    },
  },
  {
    value: 'Rejected',
    label: 'Rejected',
    icon: XCircle,
    colors: {
      bg: 'bg-red-100',
      text: 'text-red-800',
      border: 'border-red-200',
    },
  },
  {
    value: 'Saved',
    label: 'Saved',
    icon: Save,
    colors: {
      bg: 'bg-gray-100',
      text: 'text-gray-800',
      border: 'border-gray-200',
    },
  },
  {
    value: 'Submitted',
    label: 'Submitted',
    icon: Send,
    colors: {
      bg: 'bg-blue-100',
      text: 'text-blue-800',
      border: 'border-blue-200',
    },
  },
  {
    value: 'Settled',
    label: 'Settled',
    icon: DollarSign,
    colors: {
      bg: 'bg-purple-100',
      text: 'text-purple-800',
      border: 'border-purple-200',
    },
  },
  {
    value: 'Settled - Part',
    label: 'Settled - Part',
    icon: CircleDot,
    colors: {
      bg: 'bg-violet-100',
      text: 'text-violet-800',
      border: 'border-violet-200',
    },
  },
  {
    value: 'Unsettled',
    label: 'Unsettled',
    icon: AlertCircle,
    colors: {
      bg: 'bg-orange-100',
      text: 'text-orange-800',
      border: 'border-orange-200',
    },
  },
  {
    value: 'Unclaimed',
    label: 'Unclaimed',
    icon: FileQuestion,
    colors: {
      bg: 'bg-slate-100',
      text: 'text-slate-800',
      border: 'border-slate-200',
    },
  },
  {
    value: 'Claimed',
    label: 'Claimed',
    icon: UserCheck,
    colors: {
      bg: 'bg-indigo-100',
      text: 'text-indigo-800',
      border: 'border-indigo-200',
    },
  },
  {
    value: 'Approved - Part',
    label: 'Approved - Part',
    icon: CheckSquare,
    colors: {
      bg: 'bg-lime-100',
      text: 'text-lime-800',
      border: 'border-lime-200',
    },
  },
];
