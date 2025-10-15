CREATE TABLE `guild_config` (
  `p_key` BIGINT UNSIGNED NOT NULL,
  `f_key` BIGINT UNSIGNED,
  `name` VARCHAR(64),
  `cfg` JSON NOT NULL,
  PRIMARY KEY (`p_key`)
);

CREATE TABLE `oauth_user` (
    `user_id` BIGINT(20) NOT NULL,
    `api_token` VARCHAR(191),
    `username` VARCHAR(191),
    `discriminator` VARCHAR(191),
    `avatar` VARCHAR(191),
    `access_token` VARCHAR(191),
    `refresh_token` VARCHAR(191),
    `expires_at` BIGINT(20) UNSIGNED NOT NULL,
    PRIMARY KEY (`user_id`)
);

CREATE TABLE `oauth_user_guilds` (
    `user_id` BIGINT(20) NOT NULL,
    `guild_id` BIGINT(20) NOT NULL
 );

CREATE TABLE `greetings` (
  `guild_id` BIGINT(20) UNSIGNED NOT NULL,
  `user_id` BIGINT(20) UNSIGNED NOT NULL,
  `visit_count` INT UNSIGNED NOT NULL DEFAULT 0,
  PRIMARY KEY (`guild_id`, `user_id`)
);

CREATE TABLE `mbr_stats_messages` (
    `guild_id` BIGINT(20) UNSIGNED NOT NULL,
    `channel_id` BIGINT(20) UNSIGNED NOT NULL,
    `message_id` BIGINT(20) UNSIGNED NOT NULL,
    `user_id` BIGINT(20) UNSIGNED NOT NULL,
    `reply_to` BIGINT(20) UNSIGNED,
    `reply_to_user` BIGINT(20) UNSIGNED,
    `at` BIGINT(20) UNSIGNED NOT NULL,
    PRIMARY KEY (`message_id`)
);

CREATE TABLE `mbr_stats_reactions` (
    `guild_id` BIGINT(20) UNSIGNED NOT NULL,
    `message_id` BIGINT(20) UNSIGNED NOT NULL,
    `message_author_id` BIGINT(20) UNSIGNED NOT NULL,
    `user_id` BIGINT(20) UNSIGNED NOT NULL,
    `emoji` VARCHAR(191),
    `emoji_id` BIGINT(20) UNSIGNED,
    `at` BIGINT(20) UNSIGNED NOT NULL
);

CREATE TABLE `mbr_stats_presence` (
    `guild_id` BIGINT(20) UNSIGNED NOT NULL,
    `user_id` BIGINT(20) UNSIGNED NOT NULL,
    `status` VARCHAR(191) NOT NULL,
    `started_at` BIGINT(20) UNSIGNED NOT NULL,
    `ended_at` BIGINT(20) UNSIGNED NOT NULL,
    `duration` INT UNSIGNED NOT NULL
);

CREATE TABLE `mbr_stats_last_logoff` (
    `guild_id` BIGINT(20) UNSIGNED NOT NULL,
    `user_id` BIGINT(20) UNSIGNED NOT NULL,
    `at` BIGINT(20) UNSIGNED NOT NULL
);

CREATE TABLE `isolator` (
    `case_id` INT UNSIGNED NOT NULL AUTO_INCREMENT,
    `guild_id` BIGINT(20) UNSIGNED NOT NULL,
    `is_active` BOOL NOT NULL DEFAULT 1,
    `is_muted` BOOL NOT NULL DEFAULT 0,
    `user_id` BIGINT(20) UNSIGNED NOT NULL,
    `username` VARCHAR(191) NOT NULL,
    `name` VARCHAR(191),
    `at` BIGINT(20) UNSIGNED NOT NULL,
    `duration` INT UNSIGNED NOT NULL,
    `author_id` BIGINT(20) UNSIGNED NOT NULL,
    `author_username` VARCHAR(191) NOT NULL,
    `reason` VARCHAR(512),
    PRIMARY KEY (`case_id`)
);

CREATE TABLE `twitch_streams` (
    `stream_id` BIGINT(20) UNSIGNED NOT NULL,
    `user_id` BIGINT(20) UNSIGNED NOT NULL,
    `user_name` VARCHAR(128) NOT NULL,
    `user_avatar` VARCHAR(256) NOT NULL,
    `game_name` VARCHAR(256) NOT NULL,
    `game_thumbnail` VARCHAR(256) NOT NULL,
    `title` VARCHAR(512) NOT NULL,
    `started_at` BIGINT(20) UNSIGNED NOT NULL,
    `ended_at` BIGINT(20) UNSIGNED,
    `is_live` BOOL NOT NULL DEFAULT 1,
    `thumbnail` VARCHAR(512),
    `viewer_count` INT UNSIGNED NOT NULL,
    PRIMARY KEY (`stream_id`)
);

CREATE TABLE `twitch_stat` (
    `stream_id` BIGINT(20) UNSIGNED NOT NULL,
    `viewer_count` INT UNSIGNED NOT NULL,
    `at` BIGINT(20) UNSIGNED NOT NULL
);

CREATE TABLE `yt_known_channels` (
    `channel` VARCHAR(128) NOT NULL,
    PRIMARY KEY (`channel`)
);

CREATE TABLE `yt_known_videos` (
    `channel` VARCHAR(128) NOT NULL,
    `video_id` VARCHAR(128) NOT NULL,
    `video_type` VARCHAR(128) NOT NULL
);