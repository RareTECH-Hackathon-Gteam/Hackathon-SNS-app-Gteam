DROP DATABASE IF EXISTS snsapp;

DROP USER IF EXISTS 'testuser'@'%';


CREATE USER 'testuser'@'%' IDENTIFIED BY 'testuser';

CREATE DATABASE IF NOT EXISTS snsapp
  DEFAULT CHARACTER SET utf8mb4
  DEFAULT COLLATE utf8mb4_unicode_ci;


GRANT ALL PRIVILEGES ON snsapp.* TO 'testuser'@'%';

FLUSH PRIVILEGES;

USE snsapp;

CREATE TABLE
    users (
        id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
        name VARCHAR(255) NOT NULL,
        email VARCHAR(255) NOT NULL,
        password VARCHAR(255) NOT NULL,
        created_at DATETIME (6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
        updated_at DATETIME (6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
        PRIMARY KEY (id),
        UNIQUE KEY uq_users_email (email)
    ) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_unicode_ci;

CREATE TABLE
    posts (
        id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
        user_id BIGINT UNSIGNED NOT NULL,
        contents TEXT NOT NULL,
        created_at DATETIME (6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
        updated_at DATETIME (6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
        deleted_at DATETIME (6) DEFAULT NULL,
        PRIMARY KEY (id),
        KEY idx_posts_user_id (user_id),
        CONSTRAINT fk_posts_user FOREIGN KEY (user_id) REFERENCES users (id)
    ) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_unicode_ci;

CREATE TABLE 
    reactions (
        id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
        user_id BIGINT UNSIGNED NOT NULL,
        post_id BIGINT UNSIGNED NOT NULL,
        reaction_id BIGINT UNSIGNED NOT NULL,
        created_at DATETIME (6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
        PRIMARY KEY (id),
        KEY idx_reactions_user_id (user_id),
        KEY idx_reactions_post_id (post_id),
        CONSTRAINT fk_reactions_user FOREIGN KEY (user_id) REFERENCES users (id),
        CONSTRAINT fk_reactions_post FOREIGN KEY (post_id) REFERENCES posts (id),
        CONSTRAINT fk_reactions_reaction_mst FOREIGN KEY (reaction_id) REFERENCES reaction_mst (id),
        UNIQUE (user_id, post_id, reaction_id)
    ) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_unicode_ci;

CREATE TABLE
    reaction_mst (
        id BIGINT UNSIGNED NOT NULL UNIQUE,
        reaction_name CHAR(50) NOT NULL,
        PRIMARY KEY (id)
    ) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_unicode_ci;

INSERT INTO reaction_mst (id, reaction_name)
VALUES
    (1, 'good'),
    (2, 'study');

INSERT INTO users (name, email, password)
VALUES 
  ('山田太郎', 'taro@example.com', '937e8d5fbb48bd4949536cd65b8d35c426b80d2f830c5c308e2cdec422ae2244'),
  ('鈴木二郎', 'jiro@example.com', '937e8d5fbb48bd4949536cd65b8d35c426b80d2f830c5c308e2cdec422ae2244');

INSERT INTO posts (user_id, contents)
VALUES
  (1, 'こんにちは！初めての投稿です。'),
  (1, '今日はとても良い天気ですね。'),
  (1, '今日も勉強頑張ります！');


INSERT INTO comments (user_id, post_id, content)
VALUES
    (2, 1, '応援しています！頑張ってください。');