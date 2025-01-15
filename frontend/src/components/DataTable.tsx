import { Button } from '@/components/ui/button';
import * as React from 'react';
import * as XLSX from 'xlsx';
import jsPDF from 'jspdf';
import 'jspdf-autotable';
import {
  ColumnDef,
  flexRender,
  getCoreRowModel,
  getPaginationRowModel,
  useReactTable,
  SortingState,
  getSortedRowModel,
  ColumnFiltersState,
  getFilteredRowModel,
} from '@tanstack/react-table';
import { Input } from '@/components/ui/input';

import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import { Download } from 'lucide-react';
import {
  Select,
  SelectContent,
  SelectGroup,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from './ui/select';

interface DataTableProps<TData, TValue> {
  columns: ColumnDef<TData, TValue>[];
  data: TData[];
}

export function DataTable<TData, TValue>({
  columns,
  data,
}: DataTableProps<TData, TValue>) {
  const [sorting, setSorting] = React.useState<SortingState>([]);
  const [columnFilters, setColumnFilters] = React.useState<ColumnFiltersState>(
    [],
  );
  const [selectedValue, setSelectedValue] = React.useState<string>('');
  const table = useReactTable({
    data,
    columns,
    getCoreRowModel: getCoreRowModel(),
    getPaginationRowModel: getPaginationRowModel(),
    onSortingChange: setSorting,
    getSortedRowModel: getSortedRowModel(),
    onColumnFiltersChange: setColumnFilters,
    getFilteredRowModel: getFilteredRowModel(),
    state: {
      sorting,
      columnFilters,
    },
  });

  const handleExport = (format: string) => {
    setSelectedValue(format);
    if (format === 'pdf') {
      exportToPDF(data);
    } else if (format === 'xlsx') {
      exportToExcel(data);
    }else {
      return;
    }
    setSelectedValue('');
  };

  const exportToPDF = (data: any) => {
    const doc = new jsPDF();
    doc.text('Table Export', 14, 10);
    const tableHeaders = Object.keys(data[0]);
    const tableRows = data.map((item: any) => Object.values(item));
    doc.autoTable({
      head: [tableHeaders],
      body: tableRows,
    });
    doc.save('table.pdf');
  };

  const exportToExcel = (data: any) => {
    const worksheet = XLSX.utils.json_to_sheet(data);
    const workbook = XLSX.utils.book_new();
    XLSX.utils.book_append_sheet(workbook, worksheet, 'Table');

    XLSX.writeFile(workbook, 'MealRecord.xlsx');
  };

  return (
    <div>
      <div className="flex items-center justify-between space-x-2 py-4">
        <Input
          placeholder="Filter By Employee Id..."
          value={(table.getColumn('empId')?.getFilterValue() as string) ?? ''}
          onChange={(event) =>
            table.getColumn('empId')?.setFilterValue(event.target.value)
          }
          className="max-w-sm"
        />
        <Input
          placeholder="Filter By Employee Name..."
          value={(table.getColumn('empName')?.getFilterValue() as string) ?? ''}
          onChange={(event) =>
            table.getColumn('empName')?.setFilterValue(event.target.value)
          }
          className="max-w-sm"
        />
        <div onClick={() => handleExport(selectedValue)}>
          <Select
            value={selectedValue}
            onValueChange={(value) => handleExport(value)}
          >
            <SelectTrigger className="flex w-[180px] items-center gap-2 rounded-md border px-4 py-2 shadow-sm">
              <Download onClick={() => handleExport} />
              <SelectValue
                placeholder="Export As"
                className="font-medium text-gray-700"
              />
            </SelectTrigger>
            <SelectContent className="w-[180px] rounded-md border border-gray-300  shadow-lg">
              <SelectGroup>
                <SelectItem value="xlsx" className="px-4 py-2">
                  Excel
                </SelectItem>
                <SelectItem value="pdf" className="px-4 py-2">
                  PDF
                </SelectItem>
              </SelectGroup>
            </SelectContent>
          </Select>
        </div>
      </div>
      <div className="rounded-md border">
        <Table>
          <TableHeader>
            {table.getHeaderGroups().map((headerGroup) => (
              <TableRow key={headerGroup.id}>
                {headerGroup.headers.map((header) => {
                  return (
                    <TableHead key={header.id}>
                      {header.isPlaceholder
                        ? null
                        : flexRender(
                            header.column.columnDef.header,
                            header.getContext(),
                          )}
                    </TableHead>
                  );
                })}
              </TableRow>
            ))}
          </TableHeader>
          <TableBody>
            {table.getRowModel().rows?.length ? (
              table.getRowModel().rows.map((row) => (
                <TableRow
                  key={row.id}
                  data-state={row.getIsSelected() && 'selected'}
                >
                  {row.getVisibleCells().map((cell) => (
                    <TableCell key={cell.id}>
                      {flexRender(
                        cell.column.columnDef.cell,
                        cell.getContext(),
                      )}
                    </TableCell>
                  ))}
                </TableRow>
              ))
            ) : (
              <TableRow>
                <TableCell
                  colSpan={columns.length}
                  className="h-24 text-center"
                >
                  No results.
                </TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
      </div>
      <div className="flex items-center justify-end space-x-2 py-4">
        <Button
          variant="outline"
          size="sm"
          onClick={() => table.previousPage()}
          disabled={!table.getCanPreviousPage()}
        >
          Previous
        </Button>
        <Button
          variant="outline"
          size="sm"
          onClick={() => table.nextPage()}
          disabled={!table.getCanNextPage()}
        >
          Next
        </Button>
      </div>
    </div>
  );
}
