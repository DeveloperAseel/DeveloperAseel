import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.LinkedHashSet;
import java.util.Set;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

public class IOCExtractor {
    private static final Pattern URL_PATTERN = Pattern.compile(
            "\\bhttps?://[^\\s<>\"']+", Pattern.CASE_INSENSITIVE);
    private static final Pattern IP_PATTERN = Pattern.compile(
            "\\b(?:\\d{1,3}\\.){3}\\d{1,3}\\b");
    private static final Pattern EMAIL_PATTERN = Pattern.compile(
            "\\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\\.[A-Z]{2,}\\b",
            Pattern.CASE_INSENSITIVE);
    private static final Pattern SHA256_PATTERN = Pattern.compile(
            "\\b[A-F0-9]{64}\\b", Pattern.CASE_INSENSITIVE);

    public static void main(String[] args) {
        if (args.length != 1) {
            System.out.println("Usage: java IOCExtractor <text-file>");
            return;
        }

        Path inputFile = Path.of(args[0]);
        if (!Files.isRegularFile(inputFile)) {
            System.out.println("File not found: " + inputFile);
            return;
        }

        try {
            String text = Files.readString(inputFile);

            Set<String> urls = extractMatches(URL_PATTERN, text, true);
            Set<String> ipAddresses = extractValidIpAddresses(text);
            Set<String> emails = extractMatches(EMAIL_PATTERN, text, false);
            Set<String> sha256Hashes = extractMatches(SHA256_PATTERN, text, false);

            System.out.println("\n=== IOC Extraction Report ===");
            printGroup("URLs", urls);
            printGroup("IPv4 Addresses", ipAddresses);
            printGroup("Email Addresses", emails);
            printGroup("SHA-256 Hashes", sha256Hashes);

            int total = urls.size() + ipAddresses.size()
                    + emails.size() + sha256Hashes.size();
            System.out.println("\nTotal unique indicators: " + total);
        } catch (IOException error) {
            System.out.println("Could not read the file: " + error.getMessage());
        }
    }

    private static Set<String> extractMatches(
            Pattern pattern, String text, boolean cleanUrl) {
        Set<String> results = new LinkedHashSet<>();
        Matcher matcher = pattern.matcher(text);

        while (matcher.find()) {
            String value = matcher.group();
            results.add(cleanUrl ? removeTrailingPunctuation(value) : value);
        }

        return results;
    }

    private static Set<String> extractValidIpAddresses(String text) {
        Set<String> results = new LinkedHashSet<>();
        Matcher matcher = IP_PATTERN.matcher(text);

        while (matcher.find()) {
            String candidate = matcher.group();
            if (isValidIpv4(candidate)) {
                results.add(candidate);
            }
        }

        return results;
    }

    private static boolean isValidIpv4(String address) {
        String[] parts = address.split("\\.");
        for (String part : parts) {
            int number = Integer.parseInt(part);
            if (number < 0 || number > 255) {
                return false;
            }
        }
        return true;
    }

    private static String removeTrailingPunctuation(String value) {
        while (!value.isEmpty()
                && ".,;:)]}".indexOf(value.charAt(value.length() - 1)) >= 0) {
            value = value.substring(0, value.length() - 1);
        }
        return value;
    }

    private static void printGroup(String title, Set<String> values) {
        System.out.println("\n" + title + " (" + values.size() + ")");
        if (values.isEmpty()) {
            System.out.println("- None found");
            return;
        }

        for (String value : values) {
            System.out.println("- " + value);
        }
    }
}
