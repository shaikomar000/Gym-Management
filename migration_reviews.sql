-- IronPath member-review migration
-- Run this once in phpMyAdmin: select gym database > SQL > paste > Go.
-- Existing reviews are preserved; their user_id will remain NULL.
ALTER TABLE `reviews`
  ADD COLUMN `user_id` INT NULL AFTER `sno`;

CREATE INDEX `idx_reviews_user_id` ON `reviews` (`user_id`);
