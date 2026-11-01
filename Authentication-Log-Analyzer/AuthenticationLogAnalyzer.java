import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.time.Duration;
import java.time.Instant;
import java.time.format.DateTimeParseException;
import java.util.ArrayList;
import java.util.Comparator;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Locale;
import java.util.Map;

public class AuthenticationLogAnalyzer {
    record Event(Instant timestamp, String username, String source, String result) {}
    record Key(String username, String source) {}
    record Burst(Key key, int failures, Instant start, Instant end) {}
    record SuccessAfterFailures(Event success, int precedingFailures) {}

    static List<Event> readEvents(Path path) throws IOException {
        List<String> lines = Files.readAllLines(path);
        if (lines.isEmpty() || !lines.get(0).strip().equals("timestamp|username|source_ip|result")) {
            throw new IllegalArgumentException(
                    "Header must be: timestamp|username|source_ip|result");
        }
        List<Event> events = new ArrayList<>();
        for (int index = 1; index < lines.size(); index++) {
            String line = lines.get(index);
            int lineNumber = index + 1;
            if (line.isBlank()) {
                continue;
            }
            String[] fields = line.split("\\|", -1);
            if (fields.length != 4) {
                throw new IllegalArgumentException(
                        "Line " + lineNumber + " must contain exactly four pipe-separated fields");
            }
            for (int field = 0; field < fields.length; field++) {
                fields[field] = fields[field].strip();
                if (fields[field].isEmpty()) {
                    throw new IllegalArgumentException(
                            "Line " + lineNumber + " contains an empty field");
                }
            }
            String result = fields[3].toUpperCase(Locale.ROOT);
            if (!result.equals("SUCCESS") && !result.equals("FAILURE")) {
                throw new IllegalArgumentException(
                        "Line " + lineNumber + " result must be SUCCESS or FAILURE");
            }
            try {
                events.add(new Event(Instant.parse(fields[0]), fields[1], fields[2], result));
            } catch (DateTimeParseException error) {
                throw new IllegalArgumentException(
                        "Line " + lineNumber + " timestamp must be an ISO-8601 UTC instant, such as 2026-11-01T06:00:00Z");
            }
        }
        events.sort(Comparator.comparing(Event::timestamp)
                .thenComparing(Event::username).thenComparing(Event::source)
                .thenComparing(Event::result));
        return events;
    }

    static Map<Key, List<Event>> groupFailures(List<Event> events) {
        Map<Key, List<Event>> failures = new LinkedHashMap<>();
        for (Event event : events) {
            if (event.result().equals("FAILURE")) {
                Key key = new Key(event.username(), event.source());
                failures.computeIfAbsent(key, ignored -> new ArrayList<>()).add(event);
            }
        }
        return failures;
    }

    static List<Burst> findBursts(List<Event> events, int threshold, Duration window) {
        List<Burst> findings = new ArrayList<>();
        for (Map.Entry<Key, List<Event>> entry : groupFailures(events).entrySet()) {
            List<Event> failures = entry.getValue();
            int left = 0;
            int bestLeft = 0;
            int bestRight = -1;
            for (int right = 0; right < failures.size(); right++) {
                while (Duration.between(failures.get(left).timestamp(),
                        failures.get(right).timestamp()).compareTo(window) > 0) {
                    left++;
                }
                if (bestRight < bestLeft || right - left > bestRight - bestLeft) {
                    bestLeft = left;
                    bestRight = right;
                }
            }
            int count = bestRight < bestLeft ? 0 : bestRight - bestLeft + 1;
            if (count >= threshold) {
                findings.add(new Burst(entry.getKey(), count,
                        failures.get(bestLeft).timestamp(), failures.get(bestRight).timestamp()));
            }
        }
        findings.sort(Comparator.comparingInt(Burst::failures).reversed()
                .thenComparing(Burst::start).thenComparing(burst -> burst.key().username())
                .thenComparing(burst -> burst.key().source()));
        return findings;
    }

    static List<SuccessAfterFailures> findSuccessesAfterFailures(
            List<Event> events, int threshold, Duration window) {
        Map<Key, List<Event>> failures = groupFailures(events);
        List<SuccessAfterFailures> findings = new ArrayList<>();
        for (Event event : events) {
            if (!event.result().equals("SUCCESS")) {
                continue;
            }
            Instant start = event.timestamp().minus(window);
            int count = 0;
            for (Event failure : failures.getOrDefault(
                    new Key(event.username(), event.source()), List.of())) {
                if (failure.timestamp().isAfter(event.timestamp())) {
                    break;
                }
                if (!failure.timestamp().isBefore(start)) {
                    count++;
                }
            }
            if (count >= threshold) {
                findings.add(new SuccessAfterFailures(event, count));
            }
        }
        findings.sort(Comparator.comparing(finding -> finding.success().timestamp()));
        return findings;
    }

    static void printReport(List<Event> events, int threshold, int windowMinutes) {
        Duration window = Duration.ofMinutes(windowMinutes);
        List<Burst> bursts = findBursts(events, threshold, window);
        List<SuccessAfterFailures> successes =
                findSuccessesAfterFailures(events, threshold, window);
        long failures = events.stream().filter(event -> event.result().equals("FAILURE")).count();

        System.out.println("AUTHENTICATION LOG REVIEW");
        System.out.printf("Events: %d | Failures: %d | Successes: %d%n",
                events.size(), failures, events.size() - failures);
        System.out.printf("Rule: at least %d failures within %d minutes%n%n",
                threshold, windowMinutes);

        System.out.println("FAILURE BURSTS: " + bursts.size());
        for (Burst burst : bursts) {
            System.out.printf("- user=%s | source=%s | failures=%d | %s to %s%n",
                    burst.key().username(), burst.key().source(), burst.failures(),
                    burst.start(), burst.end());
        }
        if (bursts.isEmpty()) {
            System.out.println("- None found for the configured rule.");
        }

        System.out.println("\nSUCCESSES AFTER FAILURE THRESHOLD: " + successes.size());
        for (SuccessAfterFailures finding : successes) {
            Event success = finding.success();
            System.out.printf("- user=%s | source=%s | success=%s | preceding_failures=%d%n",
                    success.username(), success.source(), success.timestamp(),
                    finding.precedingFailures());
        }
        if (successes.isEmpty()) {
            System.out.println("- None found for the configured rule.");
        }
        System.out.println("\nReview indicators only. No accounts, logs, or systems were changed.");
    }

    public static void main(String[] args) {
        if (args.length == 1 && args[0].equals("--help")) {
            usage();
            return;
        }
        if (args.length > 3) {
            System.err.println("Error: too many arguments");
            usage();
            System.exit(2);
        }
        Path path = args.length > 0
                ? Path.of(args[0])
                : Path.of("sample_auth.log");
        try {
            int threshold = args.length > 1 ? Integer.parseInt(args[1]) : 5;
            int windowMinutes = args.length > 2 ? Integer.parseInt(args[2]) : 10;
            if (threshold < 2 || windowMinutes < 1) {
                throw new IllegalArgumentException(
                        "threshold must be at least 2 and window minutes at least 1");
            }
            List<Event> events = readEvents(path);
            printReport(events, threshold, windowMinutes);
        } catch (IOException | IllegalArgumentException error) {
            System.err.println("Error: " + error.getMessage());
            usage();
            System.exit(2);
        }
    }

    static void usage() {
        System.out.println("Usage: java AuthenticationLogAnalyzer.java [log-file] [threshold] [window-minutes]");
        System.out.println("Defaults: sample_auth.log, 5 failures, 10 minutes.");
    }
}
