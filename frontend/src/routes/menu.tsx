import { Logo } from '@/components/Logo';
import { TopBar } from '@/components/TopBar';
import { Button } from '@/components/ui/button';
import { Checkbox } from '@/components/ui/checkbox';
import { Input } from '@/components/ui/input';
import { createFileRoute } from '@tanstack/react-router';
import { useState } from 'react';

export const Route = createFileRoute('/menu')({
  component: RouteComponent,
});

function RouteComponent() {
  const [menu, setMenu] = useState([
    { day: 'Monday', meal: '', special: false },
    { day: 'Tuesday', meal: '', special: false },
    { day: 'Wednesday', meal: '', special: false },
    { day: 'Thursday', meal: '', special: false },
    { day: 'Friday', meal: '', special: false },
    { day: 'Saturday', meal: '', special: false },
    { day: 'Sunday', meal: '', special: false },
  ]);

  const updateMenu = (day: any, field: any, value: any) => {
    setMenu((prev) =>
      prev.map((item) =>
        item.day === day ? { ...item, [field]: value } : item,
      ),
    );
  };

  const handleSubmit = () => {
    console.log('Menu for the week:', menu);
    alert('Menu saved successfully!');
  };

  return (
    <div className="min-h-screen ">
      <TopBar
        className=" px-4 pt-3 shadow-md sm:px-8"
        leftContent={
          <div className="flex items-center gap-3">
            <Logo className="h-10 w-10 cursor-pointer sm:h-12 sm:w-12" />
            <div className="text-lg font-bold sm:text-2xl">
              hi,
            </div>
          </div>
        }
        rightContent={
          <div className="flex gap-2">
            <Button type="button" variant="outline">
              Serve
            </Button>
            <Button variant="destructive">Logout</Button>
          </div>
        }
      />

      <div className="min-h-screen ">
        <div className="mx-auto max-w-5xl space-y-4 rounded-lg p-8 ">
          <h1 className="text-3xl font-bold ">Weekly Meal Planner</h1>
          <p className="text-sm text-gray-500">
            Add meals for the week and mark special items to highlight them.
          </p>

          <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3">
            {menu.map(({ day, meal, special }) => (
              <div
                key={day}
                className="group relative flex flex-col items-start justify-between rounded-lg  p-6 shadow-md transition-transform hover:scale-105 "
              >
                <div className="absolute left-0 top-0 h-2 w-full rounded-t-lg bg-gradient-to-r from-indigo-500 via-purple-500 to-pink-500"></div>
                <h2 className="text-xl font-medium text-indigo-600">{day}</h2>
                <Input
                  placeholder={`Enter meal for ${day}`}
                  value={meal}
                  onChange={(e) => updateMenu(day, 'meal', e.target.value)}
                  className="mt-4 w-full rounded-md border border-gray-300 p-2 focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500"
                />
                <div className="mt-4 flex items-center gap-3">
                  <Checkbox
                    checked={special}
                    onCheckedChange={(checked) => {
                      console.log('hello');
                      updateMenu(day, 'special', checked);
                    }}
                    className="rounded focus:ring-indigo-500"
                  />
                  <span className="text-sm text-gray-600">Mark as Special</span>
                </div>
              </div>
            ))}
          </div>

          <div className="mt-8 text-center">
            <Button
              type="button"
              onClick={handleSubmit}
              className="rounded-lg bg-indigo-600 px-6 py-3 font-semibold text-white shadow-md transition-all hover:bg-indigo-700 hover:shadow-lg"
            >
              Save Menu
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
}
