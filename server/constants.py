TABLES_PATH = 'tables/'

EXCEL_TABLES = [
    "Дополнительная литература на каз.яз.xlsx",
    "Дополнительная литература на рус.яз.xlsx",
    "Дополнительная литература на др.яз.xlsx",
    "Методические пособия на каз.яз.xlsx",
    "Методические пособия на рус.яз.xlsx",
    "Методические пособия на др.яз.xlsx",
    "Словари на каз.яз.xlsx",
    "Словари на рус.яз.xlsx",
    "Словари на др.яз.xlsx",
    "Художественная литература на каз.яз.xlsx",
    "Художественная литература на рус.яз.xlsx",
    "Художественная литература на др.яз.xlsx",
    "Электронные издания.xlsx",
    "Энциклопедии на каз.яз.xlsx",
    "Энциклопедии на рус.яз.xlsx",
    "Энциклопедии на др.яз.xlsx"
]


class ActionCode:
    """An enum class for the action names."""
    SEARCH = "search"
    NEXT_PAGE = "next-page"
    PREV_PAGE = "prev-page"
    BOOK = "book"
    CATEGORIES = "categories"
    CATEGORY_SELECT = "category-select"
    LANGUAGE = "language"
    MAIN_MENU = "main-menu"
