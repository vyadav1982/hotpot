import { useFrappeGetDocList } from 'frappe-react-sdk';
import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';

const Menu = () => {
  const [mealPlan, setMealPlan] = useState<{ [key: string]: any }>({});
  const { data } = useFrappeGetDocList('Hotpot Menu', { fields: ['*'] });

  useEffect(() => {
    if (data) {
      const formattedMealPlan = data.reduce((acc: any, dayPlan: any) => {
        acc[dayPlan.day] = dayPlan;
        return acc;
      }, {});
      setMealPlan(formattedMealPlan);
    }
  }, [data]);

  return (
    <div className="container mx-auto p-4">
      <h1 className="mb-6 text-center text-3xl font-bold">Weekly Meal Plan</h1>
      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
        {Object.entries(mealPlan).map(([day, dayPlan]) => {
          const {
            special,
            breakfast,
            breakfast_special,
            luch,
            lunch_special,
            snacks,
            snacks_special,
            dinner,
            dinner_special,
          } = dayPlan;

          const isDaySpecial = special ? 'ring-2 ring-red-500 shadow-xl ' : '';

          return (
            <Card
              key={day}
              className={`p-4 ${isDaySpecial} transition-transform  `}
            >
              <CardHeader>
                <CardTitle className="text-xl font-semibold ">
                  {day}{' '}
                  {special === 1 ? (
                    <span className="text-red-500">🔥</span>
                  ) : null}
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {breakfast && (
                    <div
                      className={`rounded-lg p-2 ${
                        breakfast_special ? 'ring-2 ring-yellow-500' : ''
                      }`}
                    >
                      <h3 className="text-md font-bold ">Breakfast</h3>
                      <p className="">{breakfast}</p>
                    </div>
                  )}
                  {luch && (
                    <div
                      className={`rounded-lg p-2 ${
                        lunch_special ? 'ring-2 ring-yellow-500' : ''
                      }`}
                    >
                      <h3 className="text-md font-bold ">Lunch</h3>
                      <p className="">{luch}</p>
                    </div>
                  )}
                  {snacks && (
                    <div
                      className={`rounded-lg p-2 ${
                        snacks_special ? ' ring-2 ring-yellow-500' : ''
                      }`}
                    >
                      <h3 className="text-md font-bold ">Snacks</h3>
                      <p className="">{snacks}</p>
                    </div>
                  )}
                  {dinner && (
                    <div
                      className={`rounded-lg p-2 ${
                        dinner_special ? 'ring-2 ring-yellow-500' : ''
                      }`}
                    >
                      <h3 className="text-md font-bold ">Dinner</h3>
                      <p className="">{dinner}</p>
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>
          );
        })}
      </div>
    </div>
  );
};

export default Menu;
