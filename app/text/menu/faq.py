from aiogram.utils.i18n import gettext as _


async def get_faq_one() -> str:
    return _("""FAQ (Часто задаваемые вопросы) 📋

Добро пожаловать в Wishlist! 💖✨

Мы рады, что вы здесь! Ниже вы найдете ответы на самые частые вопросы, которые помогут вам быстро освоиться и начать получать удовольствие от использования нашего приложения.

Общие вопросы

1. Все ли данные конфиденциальны? 🔒
Да, все ваши данные строго конфиденциальны и зашифрованы. Мы не передаем ваши данные третьим лицам. Ваши желания видны только вам и вашему партнеру.

Желания и их выполнение

2. Как добавить желание? 🌠
Перейдите в раздел “Желания” и нажмите “Добавить желание”. Введите текст желания и сохраните его. Ваш партнер увидит его в своем списке.

3. Как узнать, какое желание выполнять? 🎲
Нажмите “Начать игру”, и одно из желаний вашего партнера будет выбрано случайным образом. У вас будет определенное время для его выполнения.

4. Видит ли партнер, какое желание я выполняю? 👀
Нет, ваш партнер не видит, какое именно желание вы выполняете, и не знает, что вы вообще выполняете какое-то желание, пока вы не уведомите его об этом.

""")


async def get_faq_two() -> str:
    return _("""
Пары и взаимодействие

5. Как создать пару? 💞
Перейдите в раздел “Пара” и нажмите “Создать запрос на пару”. Поделитесь ссылкой со своим партнером, чтобы они могли присоединиться.

6. Как посмотреть текущего партнера? 👩‍❤️‍👨
Перейдите в раздел “Пара” и нажмите “Посмотреть текущего партнера”.

7. Как отклонить текущего партнера? 🚫
Перейдите в раздел “Пара” и нажмите “Отклонить текущего партнера”.

Подписка и Режим 18+

8. Что такое режим 18+? 🔞
Режим 18+ — это эксклюзивный контент для подписчиков, включающий желания с элементами сексуальной близости. Это поможет добавить страсти и новых ощущений в ваши отношения.

9. Как активировать подписку? 💳
Перейдите в раздел “Режим 18+” и нажмите “Активировать подписку”. Следуйте инструкциям для завершения активации.

    """)
