import { Logo } from '@/components/Logo';
import { TopBar } from '@/components/TopBar';
import { Button } from '@/components/ui/button';
import { Checkbox } from '@/components/ui/checkbox';
import { Input } from '@/components/ui/input';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { createFileRoute, Link } from '@tanstack/react-router';
import { useFrappeGetDocList, useFrappePostCall } from 'frappe-react-sdk';
import { useContext, useEffect, useState } from 'react';
import { ProtectedRoute } from '@/utils/auth/ProtectedRoute';
import { useToast } from '@/hooks/use-toast';
import { UserContext } from '@/utils/auth/UserProvider';
import { useDialog } from '@/hooks/use-dialog';
import { LogOut, Menu } from 'lucide-react';

export const Route = createFileRoute('/menu')({
  component: () => (
    <ProtectedRoute>
      <RouteComponent />
    </ProtectedRoute>
  ),
});

function RouteComponent() {
  const { call: addMeal } = useFrappePostCall('hotpot.api.menu.set_menu');
  const { toast } = useToast();
  const { userName, logout } = useContext(UserContext);
  const { showConfirmDialog } = useDialog();
  const [isMenuOpen, setIsMenuOpen] = useState(false);

  const [menu, setMenu] = useState({
    Monday: { meals: {}, daySpecial: false },
    Tuesday: { meals: {}, daySpecial: false },
    Wednesday: { meals: {}, daySpecial: false },
    Thursday: { meals: {}, daySpecial: false },
    Friday: { meals: {}, daySpecial: false },
    Saturday: { meals: {}, daySpecial: false },
    Sunday: { meals: {}, daySpecial: false },
  });

  const mealTypes = ['breakfast', 'lunch', 'snacks', 'dinner'];

  const { data, error } = useFrappeGetDocList('Hotpot Menu', { fields: ['*'] });
  if (error) {
  }

  useEffect(() => {
    if (data) {
      const updatedMenu = { ...menu };
      data.forEach((item: any) => {
        updatedMenu[item.day] = {
          meals: {
            breakfast: {
              meal: item.breakfast || '',
              special: item.breakfast_special || false,
            },
            lunch: {
              meal: item.luch || '',
              special: item.lunch_special || false,
            },
            snacks: {
              meal: item.snacks || '',
              special: item.snacks_special || false,
            },
            dinner: {
              meal: item.dinner || '',
              special: item.dinner_special || false,
            },
          },
          daySpecial: item.special || false,
        };
      });
      setMenu(updatedMenu);
    }
  }, [data]);

  const updateMenu = (day: string, meal: string, field: string, value: any) => {
    setMenu((prev: any) => ({
      ...prev,
      [day]: {
        ...prev[day],
        meals: {
          ...prev[day].meals,
          [meal]: { ...prev[day].meals[meal], [field]: value },
        },
      },
    }));
  };

  const updateDaySpecial = (day: string, value: boolean) => {
    setMenu((prev: any) => ({
      ...prev,
      [day]: { ...prev[day], daySpecial: value },
    }));
  };

  const handleSubmit = async () => {
    const isValid = Object.values(menu).some(({ meals }) =>
      Object.values(meals).some((meal: any) => meal.meal.trim() !== ''),
    );

    if (!isValid) {
      toast({
        variant: 'destructive',
        title: 'Warning',
        description: 'Please select a date range.',
        className:
          'bg-red-100 text-red-600 border border-red-300 rounded-lg shadow-lg p-4 my-2 flex items-center gap-2',
      });
      return;
    }

    const { message } = await addMeal({
      data: JSON.stringify(menu, null, 2),
    });
    toast({
      title: 'Success',
      description: `Menu saved successfully!`,
      className:
        'bg-green-100 text-green-600 border border-green-300 rounded-lg shadow-lg p-4 my-2 flex items-center gap-2',
    });
  };

  const handleLogout = async () => {
    try {
      await showConfirmDialog({
        title: 'Confirm Logout',
        description: 'Are you sure you want to logout?',
        confirmLabel: 'Logout',
        variant: 'destructive',
        onConfirm: async () => {
          await logout();
        },
      });
    } catch (error) {
      console.error('Error during logout:', error);
    }
  };

  return (
    <div className="min-h-screen">
      <TopBar
        className="px-4 pt-3 sm:px-8"
        leftContent={
          <div className="flex items-center gap-3">
            <Link to="/login">
              <Logo className="h-10 w-10 cursor-pointer sm:h-12 sm:w-12" />
            </Link>
            <div className="text-lg font-bold sm:text-2xl">{userName}</div>
          </div>
        }
        rightContent={
          <div>
            <div className="flex items-center justify-between lg:hidden">
              <Button
                type="button"
                variant="outline"
                className="p-2"
                onClick={() => setIsMenuOpen(!isMenuOpen)}
              >
                <Menu className="h-5 w-5" />
              </Button>
            </div>

            {isMenuOpen && (
              <div className="absolute right-4 mt-2 space-y-2 rounded-md bg-white p-4 shadow-lg lg:hidden">
                <Link to="/dashboard" className="block">
                  <Button type="button" variant="outline" className="w-full">
                    Dashboard
                  </Button>
                </Link>
                <Link to="/server" className="block">
                  <Button type="button" variant="outline" className="w-full">
                    Serve
                  </Button>
                </Link>
                <Button
                  variant="destructive"
                  className="hidden sm:block"
                  onClick={handleLogout}
                >
                  Logout
                </Button>
                <button className="block sm:hidden" onClick={handleLogout}>
                  <LogOut className="h-5 w-5" />
                </button>
              </div>
            )}

            <div className="hidden gap-2 lg:flex">
              <Link to="/dashboard" className="w-full">
                <Button type="button" variant="outline">
                  Dashboard
                </Button>
              </Link>
              <Link to="/server" className="w-full">
                <Button type="button" variant="outline">
                  Serve
                </Button>
              </Link>
              <Button variant="destructive" onClick={handleLogout}>
                Logout
              </Button>
            </div>
          </div>
        }
      />

      <div className="mx-auto max-w-5xl space-y-4 rounded-lg p-8">
        <h1 className="text-3xl font-bold">Weekly Meal Planner</h1>
        <p className="text-sm text-gray-500">
          Add meals for the week, mark individual meals as special, and
          highlight entire days.
        </p>

        <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3">
          {Object.entries(menu).map(([day, { meals, daySpecial }]) => (
            <Card
              key={day}
              className="group p-4 shadow-md transition-transform hover:scale-105"
            >
              <CardHeader>
                <CardTitle className="flex justify-between">
                  <span className="text-xl font-semibold">{day}</span>
                  <div className="flex items-center gap-2">
                    <Checkbox
                      checked={daySpecial}
                      onCheckedChange={(checked) =>
                        updateDaySpecial(day, checked)
                      }
                    />
                    <span className="text-sm text-gray-600">Day Special</span>
                  </div>
                </CardTitle>
              </CardHeader>
              <CardContent>
                {mealTypes.map((meal) => (
                  <div key={meal} className="mb-4">
                    <div className="flex justify-between">
                      <label className="font-medium capitalize">{meal}</label>
                      <div>
                        <Checkbox
                          checked={meals[meal]?.special || false}
                          onCheckedChange={(checked) =>
                            updateMenu(day, meal, 'special', checked)
                          }
                          className="rounded focus:ring-indigo-500"
                        />
                        <span> Special</span>
                      </div>
                    </div>
                    <Input
                      placeholder={`Enter ${meal} for ${day}`}
                      value={meals[meal]?.meal || ''}
                      onChange={(e) =>
                        updateMenu(day, meal, 'meal', e.target.value)
                      }
                      className="mt-2 w-full rounded-md border border-gray-300 focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500"
                    />
                  </div>
                ))}
              </CardContent>
            </Card>
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
  );
}
