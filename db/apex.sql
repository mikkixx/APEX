SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- База данных: `apex`
--

-- --------------------------------------------------------

--
-- Структура таблицы `medical_exams`
--

CREATE TABLE `medical_exams` (
  `id` int(10) UNSIGNED NOT NULL,
  `athlete_id` int(10) UNSIGNED NOT NULL,
  `doctor_id` int(10) UNSIGNED NOT NULL,
  `exam_date` date NOT NULL,
  `exam_type` varchar(150) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Структура таблицы `medical_metrics`
--

CREATE TABLE `medical_metrics` (
  `id` int(10) UNSIGNED NOT NULL,
  `exam_id` int(10) UNSIGNED NOT NULL,
  `metric_type` varchar(100) NOT NULL,
  `value` decimal(10,2) NOT NULL,
  `unit` varchar(50) DEFAULT NULL,
  `ref_range` varchar(100) DEFAULT NULL,
  `is_critical` tinyint(1) NOT NULL DEFAULT 0
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Структура таблицы `messages`
--

CREATE TABLE `messages` (
  `id` int(10) UNSIGNED NOT NULL,
  `sender_id` int(10) UNSIGNED NOT NULL,
  `receiver_id` int(10) UNSIGNED NOT NULL,
  `text` text NOT NULL,
  `sent_at` datetime NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Структура таблицы `readiness_status`
--

CREATE TABLE `readiness_status` (
  `id` int(10) UNSIGNED NOT NULL,
  `athlete_id` int(10) UNSIGNED NOT NULL,
  `current_status` enum('здоров','устал','болен') NOT NULL,
  `initiator_id` int(10) UNSIGNED NOT NULL,
  `lock_status` enum('заблокировано','свободно') NOT NULL DEFAULT 'свободно'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Структура таблицы `recommendations`
--

CREATE TABLE `recommendations` (
  `id` int(10) UNSIGNED NOT NULL,
  `author_id` int(10) UNSIGNED NOT NULL,
  `athlete_id` int(10) UNSIGNED NOT NULL,
  `linked_entity` enum('тренировочный план','дневник нагрузок','медкарта') NOT NULL,
  `linked_entity_id` int(10) UNSIGNED NOT NULL COMMENT 'ID плана, записи дневника или осмотра',
  `text` text NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Структура таблицы `sessions`
--

CREATE TABLE `sessions` (
  `id` int(10) UNSIGNED NOT NULL,
  `plan_id` int(10) UNSIGNED NOT NULL,
  `date` date NOT NULL,
  `time` time DEFAULT NULL,
  `activity_type` varchar(100) NOT NULL,
  `duration` int(10) UNSIGNED NOT NULL COMMENT 'В минутах',
  `status` enum('запланировано','выполнено','пропущено') NOT NULL DEFAULT 'запланировано',
  `is_deleted` tinyint(1) NOT NULL DEFAULT 0
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Структура таблицы `specialist_bindings`
--

CREATE TABLE `specialist_bindings` (
  `id` int(10) UNSIGNED NOT NULL,
  `athlete_id` int(10) UNSIGNED NOT NULL,
  `specialist_id` int(10) UNSIGNED NOT NULL,
  `status` enum('активна','прекращена') NOT NULL DEFAULT 'активна',
  `is_deleted` tinyint(1) NOT NULL DEFAULT 0
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Структура таблицы `training_diary`
--

CREATE TABLE `training_diary` (
  `id` int(10) UNSIGNED NOT NULL,
  `athlete_id` int(10) UNSIGNED NOT NULL,
  `date` date NOT NULL,
  `activity_type` varchar(100) DEFAULT NULL,
  `duration` int(10) UNSIGNED DEFAULT NULL,
  `steps` int(10) UNSIGNED DEFAULT 0,
  `sleep_hours` decimal(4,2) DEFAULT NULL COMMENT 'Часы сна (допускает дробные)',
  `fatigue` tinyint(3) UNSIGNED DEFAULT NULL CHECK (`fatigue` between 1 and 10),
  `mood` tinyint(3) UNSIGNED DEFAULT NULL CHECK (`mood` between 1 and 10),
  `comment` text DEFAULT NULL,
  `is_deleted` tinyint(1) NOT NULL DEFAULT 0
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Структура таблицы `training_plans`
--

CREATE TABLE `training_plans` (
  `id` int(10) UNSIGNED NOT NULL,
  `athlete_id` int(10) UNSIGNED NOT NULL,
  `coach_id` int(10) UNSIGNED NOT NULL,
  `title` varchar(255) NOT NULL,
  `start_date` date NOT NULL,
  `end_date` date NOT NULL,
  `is_deleted` tinyint(1) NOT NULL DEFAULT 0
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Структура таблицы `users`
--

CREATE TABLE `users` (
  `id` int(10) UNSIGNED NOT NULL,
  `email` varchar(255) NOT NULL,
  `password_hash` varchar(255) NOT NULL,
  `last_name` varchar(100) NOT NULL,
  `first_name` varchar(100) NOT NULL,
  `middle_name` varchar(100) DEFAULT NULL,
  `role` enum('спортсмен','тренер','врач') NOT NULL,
  `specialization` varchar(150) DEFAULT NULL COMMENT 'Направление для спортсмена/тренера, специализация для врача',
  `photo_path` varchar(500) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Индексы сохранённых таблиц
--

--
-- Индексы таблицы `medical_exams`
--
ALTER TABLE `medical_exams`
  ADD PRIMARY KEY (`id`),
  ADD KEY `athlete_id` (`athlete_id`),
  ADD KEY `doctor_id` (`doctor_id`),
  ADD KEY `idx_exam_date` (`exam_date`);

--
-- Индексы таблицы `medical_metrics`
--
ALTER TABLE `medical_metrics`
  ADD PRIMARY KEY (`id`),
  ADD KEY `exam_id` (`exam_id`);

--
-- Индексы таблицы `messages`
--
ALTER TABLE `messages`
  ADD PRIMARY KEY (`id`),
  ADD KEY `idx_sender` (`sender_id`),
  ADD KEY `idx_receiver` (`receiver_id`);

--
-- Индексы таблицы `readiness_status`
--
ALTER TABLE `readiness_status`
  ADD PRIMARY KEY (`id`),
  ADD KEY `initiator_id` (`initiator_id`),
  ADD KEY `idx_athlete` (`athlete_id`);

--
-- Индексы таблицы `recommendations`
--
ALTER TABLE `recommendations`
  ADD PRIMARY KEY (`id`),
  ADD KEY `author_id` (`author_id`),
  ADD KEY `athlete_id` (`athlete_id`);

--
-- Индексы таблицы `sessions`
--
ALTER TABLE `sessions`
  ADD PRIMARY KEY (`id`),
  ADD KEY `plan_id` (`plan_id`),
  ADD KEY `idx_date` (`date`);

--
-- Индексы таблицы `specialist_bindings`
--
ALTER TABLE `specialist_bindings`
  ADD PRIMARY KEY (`id`),
  ADD KEY `idx_athlete` (`athlete_id`),
  ADD KEY `idx_specialist` (`specialist_id`);

--
-- Индексы таблицы `training_diary`
--
ALTER TABLE `training_diary`
  ADD PRIMARY KEY (`id`),
  ADD KEY `athlete_id` (`athlete_id`),
  ADD KEY `idx_date` (`date`);

--
-- Индексы таблицы `training_plans`
--
ALTER TABLE `training_plans`
  ADD PRIMARY KEY (`id`),
  ADD KEY `athlete_id` (`athlete_id`),
  ADD KEY `coach_id` (`coach_id`),
  ADD KEY `idx_dates` (`start_date`,`end_date`);

--
-- Индексы таблицы `users`
--
ALTER TABLE `users`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `email` (`email`);

--
-- AUTO_INCREMENT для сохранённых таблиц
--

--
-- AUTO_INCREMENT для таблицы `medical_exams`
--
ALTER TABLE `medical_exams`
  MODIFY `id` int(10) UNSIGNED NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT для таблицы `medical_metrics`
--
ALTER TABLE `medical_metrics`
  MODIFY `id` int(10) UNSIGNED NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT для таблицы `messages`
--
ALTER TABLE `messages`
  MODIFY `id` int(10) UNSIGNED NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT для таблицы `readiness_status`
--
ALTER TABLE `readiness_status`
  MODIFY `id` int(10) UNSIGNED NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT для таблицы `recommendations`
--
ALTER TABLE `recommendations`
  MODIFY `id` int(10) UNSIGNED NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT для таблицы `sessions`
--
ALTER TABLE `sessions`
  MODIFY `id` int(10) UNSIGNED NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT для таблицы `specialist_bindings`
--
ALTER TABLE `specialist_bindings`
  MODIFY `id` int(10) UNSIGNED NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT для таблицы `training_diary`
--
ALTER TABLE `training_diary`
  MODIFY `id` int(10) UNSIGNED NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT для таблицы `training_plans`
--
ALTER TABLE `training_plans`
  MODIFY `id` int(10) UNSIGNED NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT для таблицы `users`
--
ALTER TABLE `users`
  MODIFY `id` int(10) UNSIGNED NOT NULL AUTO_INCREMENT;

--
-- Ограничения внешнего ключа сохраненных таблиц
--

--
-- Ограничения внешнего ключа таблицы `medical_exams`
--
ALTER TABLE `medical_exams`
  ADD CONSTRAINT `medical_exams_ibfk_1` FOREIGN KEY (`athlete_id`) REFERENCES `users` (`id`),
  ADD CONSTRAINT `medical_exams_ibfk_2` FOREIGN KEY (`doctor_id`) REFERENCES `users` (`id`);

--
-- Ограничения внешнего ключа таблицы `medical_metrics`
--
ALTER TABLE `medical_metrics`
  ADD CONSTRAINT `medical_metrics_ibfk_1` FOREIGN KEY (`exam_id`) REFERENCES `medical_exams` (`id`);

--
-- Ограничения внешнего ключа таблицы `messages`
--
ALTER TABLE `messages`
  ADD CONSTRAINT `messages_ibfk_1` FOREIGN KEY (`sender_id`) REFERENCES `users` (`id`),
  ADD CONSTRAINT `messages_ibfk_2` FOREIGN KEY (`receiver_id`) REFERENCES `users` (`id`);

--
-- Ограничения внешнего ключа таблицы `readiness_status`
--
ALTER TABLE `readiness_status`
  ADD CONSTRAINT `readiness_status_ibfk_1` FOREIGN KEY (`athlete_id`) REFERENCES `users` (`id`),
  ADD CONSTRAINT `readiness_status_ibfk_2` FOREIGN KEY (`initiator_id`) REFERENCES `users` (`id`);

--
-- Ограничения внешнего ключа таблицы `recommendations`
--
ALTER TABLE `recommendations`
  ADD CONSTRAINT `recommendations_ibfk_1` FOREIGN KEY (`author_id`) REFERENCES `users` (`id`),
  ADD CONSTRAINT `recommendations_ibfk_2` FOREIGN KEY (`athlete_id`) REFERENCES `users` (`id`);

--
-- Ограничения внешнего ключа таблицы `sessions`
--
ALTER TABLE `sessions`
  ADD CONSTRAINT `sessions_ibfk_1` FOREIGN KEY (`plan_id`) REFERENCES `training_plans` (`id`);

--
-- Ограничения внешнего ключа таблицы `specialist_bindings`
--
ALTER TABLE `specialist_bindings`
  ADD CONSTRAINT `specialist_bindings_ibfk_1` FOREIGN KEY (`athlete_id`) REFERENCES `users` (`id`),
  ADD CONSTRAINT `specialist_bindings_ibfk_2` FOREIGN KEY (`specialist_id`) REFERENCES `users` (`id`);

--
-- Ограничения внешнего ключа таблицы `training_diary`
--
ALTER TABLE `training_diary`
  ADD CONSTRAINT `training_diary_ibfk_1` FOREIGN KEY (`athlete_id`) REFERENCES `users` (`id`);

--
-- Ограничения внешнего ключа таблицы `training_plans`
--
ALTER TABLE `training_plans`
  ADD CONSTRAINT `training_plans_ibfk_1` FOREIGN KEY (`athlete_id`) REFERENCES `users` (`id`),
  ADD CONSTRAINT `training_plans_ibfk_2` FOREIGN KEY (`coach_id`) REFERENCES `users` (`id`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
