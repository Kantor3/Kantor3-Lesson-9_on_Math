import numpy as np
import matplotlib.pyplot as plt
import scipy.stats as stats


# Математический метод нахождения коэффициентов линейной регрессии y = b_0 + b_1 * x
def LinRegression_math(X_ds, Y_ds, intercept=True, rnd=3):
    if intercept:
        # 𝑏1 = ( 𝑛*∑(𝑖=1; 𝑛) 𝑥_𝑖 𝑦_𝑖 − (∑(𝑖=1; 𝑛) 𝑥_𝑖) * (∑ (𝑖=1; 𝑛) 𝑦_𝑖) ) /
        # ( 𝑛∑_(𝑖=1; 𝑛) 𝑥_𝑖^2 − (∑(𝑖=1; 𝑛) 𝑥_𝑖)^2 )
        # b0 = 𝑦_mean − b1 * 𝑥_mean
        b1 = (np.mean(X_ds * Y_ds) - np.mean(X_ds) * np.mean(Y_ds)) / \
              (np.mean(X_ds ** 2) - np.mean(X_ds) ** 2)
        b0 = np.mean(Y_ds) - b1 * np.mean(X_ds)
    else:
        # 𝑏1 = ∑(𝑖=1; 𝑛) 𝑥_𝑖 𝑦_𝑖 / ∑_(𝑖=1; 𝑛) 𝑥_𝑖^2
        # b0 = 0
        b1 = np.sum(X_ds * Y_ds) / np.sum(X_ds ** 2)
        b0 = 0
    return round(b0, rnd), round(b1, rnd)


# Матричный метод нахождения коэффициентов линейной регрессии:
# y = b_0 + b_1 * x => Y = X * B (в матричном виде, где Y, X и B - матричное отображение данных)
# (𝑦_1 @ 𝑦_2 @ 𝑦_3) = (1 & 𝑥_1 @ 1 & 𝑥_2 @ 1 & 𝑥_3) * (𝛽_0 @ 𝛽_1)
# Откуда:
# 𝐵 = (𝑋.𝑇 ∗ 𝑋)^(−1) ∗ 𝑋.𝑇 ∗ 𝑌
#
# b0 = 𝑦_mean − b1 * 𝑥_mean
def LinRegression_matrix(x_ds, y_ds, rnd=3):
    X = x_ds.reshape(-1, 1)
    X = np.hstack([np.ones(x_ds.shape + (1,)), X])
    Y = y_ds.reshape(-1, 1)
    B = np.dot(np.linalg.inv(np.dot(X.T, X)), np.dot(X.T, Y))
    b0, b1 = B[:, 0]
    return round(b0, rnd), round(b1, rnd)


# Метод градиентного спуска:
# Очередное приближение рассчитывается по формуле:
# 1) Без intercept - B_n+1 = B_n - l_rate * (2/n) * ∑(𝑖=1; 𝑛)((B_n*X_i - Y_i) * X_i)
def LinRegression_GD(X, Y, intercept=False, rnd=3,
                     n_epochs=None, l_rate=1e-6):

    def mae_(B, Y, X, N):
        b0, b1 = B
        mae_ret = np.sum(b1 * X - Y)**2 / N if not intercept else \
                  np.sum((b0 + b1 * X) - Y)**2 / N
        return mae_ret

    N = X.size
    Y_mean      = np.mean(Y)
    Y_min       = np.min(Y)
    n_epochs    = 100 if n_epochs is None else n_epochs
    batch       = n_epochs / 20
    l_rate      = 1e-6 if l_rate is None else l_rate
    DOC_stop    = 1e-6                          # ищем пока степень изменения mae_ не станет меньше 0,001%
    B0          = 0 if not intercept else Y_min
    B1          = np.mean((Y-B0)/X)             # задаем начальное значение
    for i in range(n_epochs):
        grad_B1 = (2 / N) * np.sum((B0 + B1 * X - Y) * X)
        grad_B0 = 0 if not intercept else (2 / N) * np.sum((B0 + B1 * X - Y))
        B1 -= l_rate * grad_B1
        B0 -= l_rate * grad_B0
        mae_curr = mae_((B0, B1), Y, X, N)
        DOC_c = np.sqrt(mae_curr) / Y_mean
        if i % batch == 0 or DOC_c < DOC_stop:
            print(f'Итерация {i}: (B0, B1) = {B0, B1}, acc = {mae_curr}, изменение = {DOC_c * 100}%')
            if DOC_c < DOC_stop:
                break

    return round(B0, rnd), round(B1, rnd)


# Вывод результата расчета линейной регрессии
def print_result(X_ds, Y_ds, b0, b1, tt=None, txt_method='математический метод'):
    print('***')
    print(f'Функция линейной регрессии для {f"{tt}" if tt else f"набора данных"}:\n'
          f'X = {X_ds}\n'
          f'Y = {Y_ds}\n'
          f'Y = {b0} + {b1} * X - использован {txt_method}')


# Показать графическую зависимость между наборами данных и рассчитанную функцию лин. регрессии
def show_XY(X_ds, Y_ds, y_func=None,
            not_label=None, not_legend=None,
            tt=None, splot=None, show_plots=True):
    tt = 'Набор зависимых данных y = F(x)' if tt is None else tt
    if splot is None:
        splot = plt
        splot.title(tt)
        splot.xlabel('данные X')
        splot.ylabel('зависимые данные Y')
    else:
        splot.set_title(tt)
        if not not_label:
            splot.set_xlabel('данные X')
            splot.set_ylabel('зависимые данные Y')

    splot.scatter(X_ds, Y_ds, label='Данные наборов X, Y')
    if y_func:
        y_f = y_func.replace('x', 'X_ds')
        splot.plot(X_ds, eval(y_f), color='r', label=f'Лин.регрессия y = {y_func}')
    if not not_legend: splot.legend()
    if show_plots:
        plt.show()


"""
Решение заданий Практики к Уроку-9
"""

# Задание-1.
# Даны значения величины заработной платы заемщиков банка (zp) и
# значения их поведенческого кредитного скоринга (ks):
# zp = [35, 45, 190, 200, 40, 70, 54, 150, 120, 110],
# ks = [401, 574, 874, 919, 459, 739, 653, 902, 746, 832].
# Используя математические операции, посчитать коэффициенты линейной регрессии,
# приняв за X заработную плату (то есть, zp - признак),
# а за y - значения скорингового балла (то есть, ks - целевая переменная).
# Произвести расчет как с использованием intercept, так и без.

# Набор данных Кредитный скоринг:
tit = 'Кредитный скоринг'
zp = np.array([35,   45, 190, 200, 40,   70,  54, 150, 120, 110])
ks = np.array([401, 574, 874, 919, 459, 739, 653, 902, 746, 832])

# Результат:
print('\n--------------------------------------------')
print(f'Задание-1. {tit}:')
print('X - Заработная плата')
print('Y - Cкоринговый балл')

print('\n1) Линейная регрессия с использованием intercept:')
b_0, b_1    = LinRegression_math(zp, ks)                 # используем математическую формулу
b_0m, b_1m  = LinRegression_matrix(zp, ks)               # используем матричные вычисления
print_result(zp, ks, b_0, b_1, tt=tit, txt_method='математический метод')
print_result(zp, ks, b_0m, b_1m, tt=tit, txt_method='матричный метод')
show_XY(zp, ks, tt=tit, y_func=f'{b_0} + {b_1} * x')

print('\n2) Линейная регрессия без использования intercept:')
b_0, b_1   = LinRegression_math(zp, ks, intercept=False, rnd=5)     # используем математическую формулу
print_result(zp, ks, b_0, b_1, tt=tit, txt_method='математический метод')
show_XY(zp, ks, tt=tit, y_func=f'{b_0} + {b_1} * x')

R = np.corrcoef(zp, ks) ** 2                                        # коэффициент детерминации
print(f'\nКоэффициент детерминации R = {round(R[0,1], 4)}')


# Задание-2.
# Посчитать коэффициент линейной регрессии при заработной плате (zp),
# используя градиентный спуск (без intercept)..
print()
print('\n--------------------------------------------')
print(f'Задание-2. {tit}:')
print('\nЛинейная регрессия без использования intercept:')
b_0, b_1 = LinRegression_GD(zp, ks, intercept=False, rnd=5,
                            n_epochs=10000, l_rate=1e-5)         # используем метод градиентного спуска
print_result(zp, ks, b_0, b_1, tt=tit, txt_method='метод градиентного спуска')


# Задание-3.
# Произвести вычисления как в пункте 2, но с вычислением intercept.
# Учесть, что изменение коэффициентов должно производиться на каждом шаге одновременно
# (то есть изменение одного коэффициента не должно влиять на изменение другого во время одной итерации).
print()
print('\n--------------------------------------------')
print(f'Задание-3. {tit}:')
print('\nЛинейная регрессия c использованием intercept:')
b_0, b_1 = LinRegression_GD(zp, ks, intercept=True, rnd=3,
                            n_epochs=1000000, l_rate=3e-5)         # используем метод градиентного спуска
print_result(zp, ks, b_0, b_1, tt=tit, txt_method='метод градиентного спуска')

exit()


"""
Решение заданий семинара к Уроку-9
"""

# Задание-1 Семинара
# Постройте графики для приведенных наборов данных. Найдите коэффициенты для линии
# регрессии и коэффициенты детерминации. Что вы замечаете? Нанесите на график модель
# линейной регрессии.
# X1= np.array([30,30,40, 40])
# Y1= np.array([37, 47, 50, 60])
# x2= np.array([30,30,40, 40, 20, 20, 50, 50])
# y2= np.array([37, 47, 50, 60, 25, 35, 62, 72])
# X3 = np.array([30,30,40, 40, 20, 20, 50, 50, 10, 10, 60, 60])
# Y3 = np.array([37, 47, 50, 60, 25, 35, 62, 72, 13, 23, 74, 84])


# 1. Набор данных №1:
# show_dataset(X1, Y1, tt='Набор данных №1')
tit = 'Набор данных №1'
X1 = np.array([30, 30, 40, 40])
Y1 = np.array([37, 47, 50, 60])
b_0, b_1 = LinRegression_math(X1, Y1, rnd=3)            # используем математическую формулу
R = np.corrcoef(X1, Y1) ** 2                            # коэффициент детерминации

# Результат:
# print(f'Коэффициент детерминации R:\n{R}')
print_result(X1, Y1, b_0, b_1, tt=tit)                  # функция линейной регрессии
print(f'Коэффициент детерминации R = {round(R[0, 1], 4)}')
show_XY(X1, Y1, tt=tit, y_func=f'{b_0} + {b_1} * x')    # графическое отображение

# 2. Набор данных №2:
tit = 'Набор данных №2'
x2 = np.array([30,30,40, 40, 20, 20, 50, 50])
y2 = np.array([37, 47, 50, 60, 25, 35, 62, 72])
b_0, b_1 = LinRegression_math(x2, y2)                   # используем математическую формулу
R = np.corrcoef(x2, y2) ** 2                            # коэффициент детерминации

# Результат:
print_result(x2, y2, b_0, b_1, tt=tit)
print(f'Коэффициент детерминации R = {round(R[0, 1], 4)}')
show_XY(x2, y2, tt=tit, y_func=f'{b_0} + {b_1} * x')


# 3. Набор данных №3:
tit = 'Набор данных №3'
X3 = np.array([30,30,40, 40, 20, 20, 50, 50, 10, 10, 60, 60])
Y3 = np.array([37, 47, 50, 60, 25, 35, 62, 72, 13, 23, 74, 84])
b_0, b_1    = LinRegression_math(X3, Y3)                        # используем математическую формулу
b_0m, b_1m  = LinRegression_matrix(X3, Y3)                      # используем матричные вычисления

R = np.corrcoef(X3, Y3) ** 2                                    # коэффициент детерминации

# Результат:
print_result(X3, Y3, b_0, b_1, tt=tit)
print_result(X3, Y3, b_0m, b_1m, tt=tit, txt_method='матричный метод')
print(f'Коэффициент детерминации R = {round(R[0, 1], 4)}')
show_XY(X3, Y3, tt=tit, y_func=f'{b_0} + {b_1} * x')


# ---------------------------------------------------------------------------------
# Задание-2 Семинара
# Проверить применимость линейной регрессии к наборам данных:
x = np.array([10, 8, 13, 9, 11, 14, 6, 4, 12, 7, 5])
y1 = np.array([8.04, 6.95, 7.58, 8.81, 8.33, 9.96, 7.24, 4.26, 10.84, 4.82, 5.68 ])
# ... x= np.array([ 10,8, 13, 9,11,14, 6,4,12, 7,5 ])
y2 = np.array([ 9.14, 8.14, 8.74,8.77, 9.26, 8.10, 6.13, 3.10, 9.13, 7.26, 4.74])
# ... x= np.array([ 10,8, 13, 9,11,14, 6,4,12, 7,5 ])
y3 = np.array([7.46,6.77, 12.74, 7.11, 7.81, 8.84, 6.08, 5.39, 8.15, 6.42, 5.73])
x4 = np.array([8, 8, 8, 8, 8, 8, 8, 19, 8, 8, 8])
y4 = np.array([6.58, 5.76, 7.71, 8.84, 8.47, 7.04, 5.25,12.5, 5.56, 7.91, 6.89])
x0 = np.array([ 10, 8, 13, 9, 11, 14, 6, 4, 12, 7,5, 15, 16, 18 ])
y0 = np.array([ 9.14, 8.14, 8.74,8.77, 9.26, 8.10, 6.13, 3.10, 9.13, 7.26, 4.74, 6.5, 5, 2.9])

# Выведем графики всех наборов для визуального анализа
_, ax = plt.subplots(2, 3)
show_XY(x, y1, tt='Данные (x, y1)', splot=ax[0, 0],
        not_label=True, not_legend=True, show_plots=False)      # Данные (x, y1)
show_XY(x, y2, tt='Данные (x, y2)', splot=ax[0, 1],
        not_label=True, not_legend=True, show_plots=False)     # Данные (x, y2)
show_XY(x, y3, tt='Данные (x, y3)', splot=ax[0, 2],
        not_label=True, not_legend=True, show_plots=False)     # Данные (x, y3)
show_XY(x4, y4, tt='Данные (x4, y4)', splot=ax[1, 0],
        not_label=False, not_legend=True, show_plots=False)     # Данные (x4, y4)
show_XY(x0, y0, tt='Данные (x0, y0)', splot=ax[1, 1],
        not_label=False, not_legend=True, show_plots=False)     # Данные (x0, y0)
plt.show()

# Рассчитаем регрессию для подходящих наборов данных (1-й и 3-й)
_, ax = plt.subplots(1, 2)

b_0m, b_1m  = LinRegression_matrix(x, y1)                      # используем матричные вычисления
R = np.corrcoef(x, y1) ** 2                                    # коэффициент детерминации
tit = 'Данные (x, y1)'
print_result(x, y1, b_0m, b_1m, tt=tit, txt_method='матричный метод')
print(f'Коэффициент детерминации R = {round(R[0, 1], 4)}')
show_XY(x, y1, tt=tit, y_func=f'{b_0m} + {b_1m} * x', splot=ax[0], show_plots=False)

b_0m, b_1m  = LinRegression_matrix(x, y3)                      # используем матричные вычисления
R = np.corrcoef(x, y3) ** 2                                    # коэффициент детерминации
tit = 'Данные (x, y3)'
print_result(x, y3, b_0m, b_1m, tt=tit, txt_method='матричный метод')
print(f'Коэффициент детерминации R = {round(R[0, 1], 4)}')
show_XY(x, y3, tt=tit, y_func=f'{b_0m} + {b_1m} * x', splot=ax[1], show_plots=False)
plt.show()

# исключим для 3-го набора выброс и посмотрим, что вышло:
x = np.array([10, 8, 9, 11, 14, 6, 4, 12, 7, 5])
y3 = np.array([7.46, 6.77, 7.11, 7.81, 8.84, 6.08, 5.39, 8.15, 6.42, 5.73])
b_0m, b_1m  = LinRegression_matrix(x, y3)                      # используем матричные вычисления
R = np.corrcoef(x, y3) ** 2                                    # коэффициент детерминации
tit = 'Данные (x, y3)'
print_result(x, y3, b_0m, b_1m, tt=tit, txt_method='матричный метод')
print(f'Коэффициент детерминации R = {round(R[0, 1], 4)}')
show_XY(x, y3, tt=tit, y_func=f'{b_0m} + {b_1m} * x')


# Тестирование 1-го набора данных на нормальность
x = np.array([10, 8, 13, 9, 11, 14, 6, 4, 12, 7, 5])
y1 = np.array([8.04, 6.95, 7.58, 8.81, 8.33, 9.96, 7.24, 4.26, 10.84, 4.82, 5.68 ])
# y3 = np.array([7.46, 6.77, 12.74, 7.11, 7.81, 8.84, 6.08, 5.39, 8.15, 6.42, 5.73])
b_0m, b_1m  = LinRegression_matrix(x, y1)                      # используем матричные вычисления
y1_pred = b_0m + b_1m * x
res = y1 - y1_pred          # массив остатков

shap = stats.shapiro(res)
print()
print(f'Тест Шапиро => {shap}')
show_XY(y1_pred, res, tt='Остатки от лин.регрессии')


# Анализ статистической значимости полученной модели линейной регрессии
# Используем критерий Фишера:
# 1) Уровень значимости критерия - стандартный α =0,05
# Для сравнения используется односторонний тест, при котором
# полученное значение критерия должно быть больше критического значения
# для выбранного уровня значимости и степеней свободы анализируемых данных.
# Критерий Фишера:
# Fр = MSф / MSo
# Здесь MSф (фактическая сумма квадратных отклонений на 1 степень свободы) = SSf / df1
# df1 - степень свободы числителя = p - 1, p - число анализируемых параметров (выборок = 2)
# Здесь MSo (остаточная сумма квадратных отклонений на 1 степень свободы) = SSo / df2
# df2 - степень свободы знаменателя = n - p, p - число парных измерений (для 1-го набора данных = 11)

# Выполним расчет для 1-го набора:
alfa = 0.05
y1_pred = b_0m + b_1m * x
SSf = np.sum((y1_pred - np.mean(y1))**2)
SSo = np.sum((y1 - y1_pred)**2)
pp = 2          # 2-а параметра участвуют в анализе
nn = len(x)     # число попарных измерений
df1 = pp - 1
df2 = nn - pp
MSf = SSf / df1
MSo = SSo / df2
Fsh = MSf / MSo
F_lim = stats.f.ppf(1 - alfa, df1, df2)
print()
print(f'-----------------------------\n'
      f'Критерий Фишера = {Fsh}\n'
      f'Значение по дов.интервалу = {F_lim}')
txt_con1 = 'Модель статистически значима'
txt_con2 = 'Зависимость определена случайными факторами'
print(txt_con1 if Fsh > F_lim else txt_con2)

