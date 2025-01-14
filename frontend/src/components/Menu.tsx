import { useFrappeGetDocList } from 'frappe-react-sdk';
import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';

const Menu = () => {
  const [mealPlan, setMealPlan] = useState<{ [key: string]: any }>({}); 
  const { data } = useFrappeGetDocList('Hotpot Menu', { fields: ['*'] });

  useEffect(() => {
    if (data) {
      console.log(data);
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
            lunch,
            lunch_special,
            snacks,
            snacks_special,
            dinner,
            dinner_special,
          } = dayPlan;

          const isDaySpecial = special ? 'ring-2 ring-red-500 shadow-xl animate-bounce' : '';

          return (
            <Card
              key={day}
              className={`p-4 ${isDaySpecial} transition-transform hover:scale-105 `}
            >
              <CardHeader>
                <CardTitle className="text-xl font-semibold text-gray-800">
                  {day} {special && <span className="text-red-500">🔥</span>}
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
                      <h3 className="text-md font-bold text-gray-700">
                        Breakfast
                      </h3>
                      <p className="text-gray-600">{breakfast}</p>
                    </div>
                  )}
                  {lunch && (
                    <div
                      className={`rounded-lg p-2 ${
                        lunch_special ? 'ring-2 ring-yellow-500' : ''
                      }`}
                    >
                      <h3 className="text-md font-bold text-gray-700">Lunch</h3>
                      <p className="text-gray-600">{lunch}</p>
                    </div>
                  )}
                  {snacks && (
                    <div
                      className={`rounded-lg p-2 ${
                        snacks_special ? 'ring-2 ring-yellow-500' : ''
                      }`}
                    >
                      <h3 className="text-md font-bold text-gray-700">
                        Snacks
                      </h3>
                      <p className="text-gray-600">{snacks}</p>
                    </div>
                  )}
                  {dinner && (
                    <div
                      className={`rounded-lg p-2 ${
                        dinner_special ? 'ring-2 ring-yellow-500 animate-pulse' : ''
                      }`}
                    >
                      <h3 className="text-md font-bold text-gray-700">
                        Dinner
                      </h3>
                      <p className="text-gray-600">{dinner}</p>
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
